"""Core combat resolution engine for AETHERMOOR.

Handles:
  - Initiative rolling and turn-order determination
  - Action resolution (attack, flee)
  - NPC AI (simple: always attacks player)
  - End-of-round condition ticking
  - Combat termination (win/die/flee)
"""
from __future__ import annotations

import random
import uuid

from dnd_combat import (
    ability_modifier,
    add_condition,
    apply_condition_tick,
    attack_advantage_from_conditions,
    flee_check,
    resolve_attack,
    roll,
    roll_initiative,
    xp_for_cr,
    ConditionType,
    WeaponType,
)
from schemas import (
    ActionType,
    CombatAction,
    CombatState,
    CombatStatus,
    Combatant,
    InitiativeEntry,
    StartCombatRequest,
)


def start_combat(req: StartCombatRequest) -> CombatState:
    """Initialise a new combat encounter from a StartCombatRequest.

    Rolls initiative for all combatants and establishes turn order.
    """
    combat_id = str(uuid.uuid4())

    player = Combatant(
        id=req.character_id,
        name=req.character_name,
        is_player=True,
        character_class=req.character_class,
        level=req.character_level,
        hp=req.character_hp,
        max_hp=req.character_max_hp,
        ac=req.character_ac,
        weapon=req.character_weapon,
        stats=req.character_stats,
    )

    npc_id = f"npc:{req.npc_template_id}"
    npc = Combatant(
        id=npc_id,
        name=req.npc_name,
        is_player=False,
        character_class="Monster",
        level=max(1, int(req.npc_cr * 2)),
        hp=req.npc_hp,
        max_hp=req.npc_max_hp,
        ac=req.npc_ac,
        weapon=req.npc_weapon,
        stats=req.npc_stats,
        cr=req.npc_cr,
        gold_drop_min=req.npc_gold_drop_min,
        gold_drop_max=req.npc_gold_drop_max,
    )

    # Roll initiative
    player_init, player_raw = roll_initiative(player.stats.dexterity)
    npc_init, npc_raw = roll_initiative(npc.stats.dexterity)

    initiative_rolls = {
        player.id: InitiativeEntry(
            combatant_id=player.id, initiative=player_init, raw_roll=player_raw
        ),
        npc_id: InitiativeEntry(
            combatant_id=npc_id, initiative=npc_init, raw_roll=npc_raw
        ),
    }

    # Sort by initiative descending; tie-break by higher DEX then random
    order = sorted(
        [player.id, npc_id],
        key=lambda cid: (
            initiative_rolls[cid].initiative,
            player.stats.dexterity if cid == player.id else npc.stats.dexterity,
            random.random(),
        ),
        reverse=True,
    )

    return CombatState(
        id=combat_id,
        zone_id=req.zone_id,
        status=CombatStatus.ACTIVE,
        round=1,
        turn_order=order,
        current_turn_index=0,
        combatants={player.id: player, npc_id: npc},
        initiative_rolls=initiative_rolls,
        action_log=[],
        player_character_id=req.character_id,
        npc_template_id=req.npc_template_id,
    )


def _get_player_id(state: CombatState) -> str:
    """Return the player combatant ID from the state."""
    for cid, c in state.combatants.items():
        if c.is_player:
            return cid
    raise ValueError("No player combatant in combat state")


def _get_npc_id(state: CombatState) -> str:
    """Return the NPC combatant ID from the state."""
    for cid, c in state.combatants.items():
        if not c.is_player:
            return cid
    raise ValueError("No NPC combatant in combat state")


def _current_combatant_id(state: CombatState) -> str:
    return state.turn_order[state.current_turn_index % len(state.turn_order)]


def _advance_turn(state: CombatState) -> CombatState:
    """Move to the next combatant in the turn order.

    When all combatants have acted, increment the round and tick conditions.
    """
    next_index = state.current_turn_index + 1

    if next_index >= len(state.turn_order):
        # End of round — tick conditions on all combatants
        updated_combatants = {}
        for cid, combatant in state.combatants.items():
            new_conditions, bleed_dmg = apply_condition_tick(combatant.conditions)
            new_hp = max(0, combatant.hp - bleed_dmg)
            updated_combatants[cid] = combatant.model_copy(
                update={"conditions": new_conditions, "hp": new_hp}
            )
        state = state.model_copy(
            update={
                "round": state.round + 1,
                "current_turn_index": 0,
                "combatants": updated_combatants,
            }
        )
    else:
        state = state.model_copy(update={"current_turn_index": next_index})

    return state


def _build_action(
    round_num: int,
    acting_id: str,
    action_type: str,
    target_id: str | None,
    roll_result: dict | None,
    description: str,
) -> CombatAction:
    return CombatAction(
        round=round_num,
        acting_id=acting_id,
        action_type=action_type,
        target_id=target_id,
        roll_result=roll_result,
        description=description,
    )


# ── Player action: ATTACK ────────────────────────────────────────────────────

def player_attack(state: CombatState, target_id: str) -> tuple[CombatState, CombatAction]:
    """Resolve a player attack action against the target."""
    player_id = _get_player_id(state)
    player = state.combatants[player_id]
    target = state.combatants[target_id]

    from dnd_combat import attack_stat_for_class
    stat_name = attack_stat_for_class(player.character_class)
    stat_score = getattr(player.stats, stat_name, player.stats.strength)

    adv, dis = attack_advantage_from_conditions(player.conditions, target.conditions)

    result = resolve_attack(
        attacker_level=player.level,
        attacker_stat_score=stat_score,
        weapon_type=player.weapon,
        target_ac=target.ac,
        advantage=adv,
        disadvantage=dis,
    )

    new_target_hp = max(0, target.hp - result["damage"])
    updated_target = target.model_copy(update={"hp": new_target_hp})
    updated_combatants = {**state.combatants, target_id: updated_target}

    hit_word = {
        "crit": "CRITICAL HIT",
        "hit": "hits",
        "miss": "misses",
        "crit_miss": "CRITICAL MISS",
    }.get(result["result"], "attacks")

    description = (
        f"{player.name} {hit_word} {target.name} "
        f"(d20={result['d20_roll']}+{result['attack_bonus']} vs AC {target.ac})"
    )
    if result["damage"] > 0:
        description += f" for {result['damage']} damage"

    action = _build_action(
        round_num=state.round,
        acting_id=player_id,
        action_type=ActionType.ATTACK,
        target_id=target_id,
        roll_result=result,
        description=description,
    )

    new_state = state.model_copy(
        update={"combatants": updated_combatants, "action_log": state.action_log + [action]}
    )
    return new_state, action


# ── Player action: FLEE ──────────────────────────────────────────────────────

def player_flee(state: CombatState) -> tuple[CombatState, CombatAction]:
    """Resolve a flee attempt.

    DEX contest: player vs NPC. Player succeeds on tie.
    """
    player_id = _get_player_id(state)
    npc_id = _get_npc_id(state)
    player = state.combatants[player_id]
    npc = state.combatants[npc_id]

    success, player_roll, npc_roll = flee_check(
        player.stats.dexterity, npc.stats.dexterity
    )

    description = (
        f"{player.name} attempts to flee "
        f"(DEX {player_roll} vs {npc.name} DEX {npc_roll}) — "
        f"{'ESCAPED' if success else 'BLOCKED'}"
    )

    action = _build_action(
        round_num=state.round,
        acting_id=player_id,
        action_type=ActionType.FLEE,
        target_id=None,
        roll_result={"player_roll": player_roll, "npc_roll": npc_roll, "success": success},
        description=description,
    )

    if success:
        new_state = state.model_copy(
            update={
                "status": CombatStatus.PLAYER_FLED,
                "action_log": state.action_log + [action],
            }
        )
    else:
        new_state = state.model_copy(
            update={"action_log": state.action_log + [action]}
        )

    return new_state, action


# ── NPC AI turn ──────────────────────────────────────────────────────────────

def npc_take_turn(state: CombatState) -> tuple[CombatState, CombatAction]:
    """Simple NPC AI: always attacks the player.

    If NPC is stunned, it skips its turn.
    """
    npc_id = _get_npc_id(state)
    player_id = _get_player_id(state)
    npc = state.combatants[npc_id]
    player = state.combatants[player_id]

    # Stunned NPC skips turn
    from dnd_combat import has_condition
    if has_condition(npc.conditions, ConditionType.STUNNED):
        action = _build_action(
            round_num=state.round,
            acting_id=npc_id,
            action_type="skip",
            target_id=None,
            roll_result=None,
            description=f"{npc.name} is stunned and cannot act.",
        )
        new_state = state.model_copy(update={"action_log": state.action_log + [action]})
        return new_state, action

    # NPC attacks player
    npc_stat_name = "strength"  # All NPCs use STR for melee in alpha
    stat_score = getattr(npc.stats, npc_stat_name, npc.stats.strength)

    adv, dis = attack_advantage_from_conditions(npc.conditions, player.conditions)

    result = resolve_attack(
        attacker_level=npc.level,
        attacker_stat_score=stat_score,
        weapon_type=npc.weapon,
        target_ac=player.ac,
        advantage=adv,
        disadvantage=dis,
    )

    new_player_hp = max(0, player.hp - result["damage"])

    # Bite: apply bleeding on hit
    new_player_conditions = list(player.conditions)
    if npc.weapon == WeaponType.BITE and result["result"] in ("hit", "crit"):
        new_player_conditions = add_condition(new_player_conditions, ConditionType.BLEEDING)

    updated_player = player.model_copy(
        update={"hp": new_player_hp, "conditions": new_player_conditions}
    )
    updated_combatants = {**state.combatants, player_id: updated_player}

    hit_word = {
        "crit": "CRITICAL HIT",
        "hit": "hits",
        "miss": "misses",
        "crit_miss": "CRITICAL MISS",
    }.get(result["result"], "attacks")

    description = (
        f"{npc.name} {hit_word} {player.name} "
        f"(d20={result['d20_roll']}+{result['attack_bonus']} vs AC {player.ac})"
    )
    if result["damage"] > 0:
        description += f" for {result['damage']} damage"

    action = _build_action(
        round_num=state.round,
        acting_id=npc_id,
        action_type=ActionType.ATTACK,
        target_id=player_id,
        roll_result=result,
        description=description,
    )

    new_state = state.model_copy(
        update={"combatants": updated_combatants, "action_log": state.action_log + [action]}
    )
    return new_state, action


# ── Combat end checks ────────────────────────────────────────────────────────

def _roll_gold_drop(npc: Combatant) -> int:
    if npc.gold_drop_max <= 0:
        return 0
    return random.randint(npc.gold_drop_min, npc.gold_drop_max)


def check_combat_end(state: CombatState) -> CombatState:
    """Check if combat has ended and set status + rewards accordingly."""
    player_id = _get_player_id(state)
    npc_id = _get_npc_id(state)
    player = state.combatants[player_id]
    npc = state.combatants[npc_id]

    if state.status != CombatStatus.ACTIVE:
        return state  # Already resolved

    if npc.hp <= 0:
        xp = xp_for_cr(npc.cr)
        gold = _roll_gold_drop(npc)
        return state.model_copy(
            update={
                "status": CombatStatus.PLAYER_WON,
                "xp_awarded": xp,
                "gold_awarded": gold,
            }
        )

    if player.hp <= 0:
        return state.model_copy(update={"status": CombatStatus.PLAYER_DIED})

    return state


# ── Main action dispatcher ───────────────────────────────────────────────────

def process_player_action(
    state: CombatState,
    action_type: ActionType,
    target_id: str | None = None,
) -> tuple[CombatState, CombatAction, CombatAction | None]:
    """Process a player action and run the NPC turn.

    Returns (updated_state, player_action, npc_action_or_None).
    NPC acts immediately after the player if combat is still active.
    """
    if state.status != CombatStatus.ACTIVE:
        raise ValueError(f"Combat {state.id} is not active (status={state.status})")

    npc_id = _get_npc_id(state)
    effective_target = target_id or npc_id

    # Player action
    if action_type == ActionType.ATTACK:
        state, player_action = player_attack(state, effective_target)
    elif action_type == ActionType.FLEE:
        state, player_action = player_flee(state)
    else:
        raise ValueError(f"Unsupported action type: {action_type}")

    # Check end after player action
    state = check_combat_end(state)
    if state.status != CombatStatus.ACTIVE:
        return state, player_action, None

    # NPC takes its turn
    state, npc_action = npc_take_turn(state)

    # Check end after NPC action
    state = check_combat_end(state)

    # Advance to next round (simple 1v1: each exchange = 1 round)
    state = _advance_turn(state)
    if _current_combatant_id(state) != _get_player_id(state):
        state = _advance_turn(state)

    return state, player_action, npc_action

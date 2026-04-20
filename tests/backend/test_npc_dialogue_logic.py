import asyncio
import unittest
import sys
import os

# Ensure quest service modules can import their own database.Base
quest_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../services/quest'))
if quest_path not in sys.path:
    sys.path.insert(0, quest_path)

# Provide a minimal in-memory database URL for SQLAlchemy to initialize the quest db layer
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from services.quest.models import QuestStatus


class _FakeQueryResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return self

    def all(self):
        return self._items


class _FakeSession:
    def __init__(self, results):
        self._results = results
        self._idx = 0

    async def execute(self, query):
        res = self._results[self._idx]
        self._idx += 1
        return _FakeQueryResult(res)


class _FakeQuest:
    def __init__(self, id, title, prerequisites, briefing_dialogue, npc_giver, is_active, sort_order, completion_dialogue=None):
        self.id = id
        self.title = title
        self.prerequisites = prerequisites
        self.briefing_dialogue = briefing_dialogue
        self.npc_giver = npc_giver
        self.is_active = is_active
        self.sort_order = sort_order
        self.completion_dialogue = completion_dialogue or ""


class _FakeCharacterQuest:
    def __init__(self, quest_id, status, objectives):
        self.quest_id = quest_id
        self.status = status
        self.objectives = objectives


class TestNPCDialogueLogic(unittest.TestCase):
    def _run_async(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_dialogue_offfer_path(self):
        # Prepare fake data: one quest available with no prerequisites
        quest = _FakeQuest(
            id="Q1",
            title="Starter Quest",
            prerequisites=[],
            briefing_dialogue="Do this to begin.",
            npc_giver="npc1",
            is_active=True,
            sort_order=0,
        )
        fake_session = _FakeSession(results=[[quest], [], []])

        async def _call():
            from services.quest.routers import npc as npc_router
            # Bypass auth by passing a dummy _user
            result = await npc_router.get_npc_dialogue(npc_id="npc1", character_id="char1", db=fake_session, _user={"id": "u1"})
            return result

        res = self._run_async(_call())
        self.assertIsNotNone(res)
        self.assertTrue(len(res.options) == 1)
        opt = res.options[0]
        self.assertEqual(opt.quest_id, "Q1")
        self.assertEqual(opt.type, "offer")
        self.assertEqual(opt.dialogue, quest.briefing_dialogue)

    def test_dialogue_no_quests_raises_404(self):
        # No quests for this NPC should raise 404
        fake_session = _FakeSession(results=[[] , [], []])

        async def _call():
            from services.quest.routers import npc as npc_router
            try:
                await npc_router.get_npc_dialogue(npc_id="npc0", character_id="char1", db=fake_session, _user={"id": "u1"})
            except Exception as exc:
                return exc
            return None

        exc = self._run_async(_call())
        self.assertIsNotNone(exc)
        self.assertEqual(exc.__class__.__name__, 'HTTPException')

    def test_dialogue_in_progress_path(self):
        quest = _FakeQuest(
            id="Q2",
            title="Progress Quest",
            prerequisites=[],
            briefing_dialogue="",
            npc_giver="npc1",
            is_active=True,
            sort_order=0,
            completion_dialogue="Well done!",
        )
        cq = _FakeCharacterQuest(quest_id="Q2", status=QuestStatus.IN_PROGRESS, objectives=[{"current": 1, "required": 2}])
        fake_session = _FakeSession(results=[[quest], [cq], []])

        async def _call():
            from services.quest.routers import npc as npc_router
            result = await npc_router.get_npc_dialogue(npc_id="npc1", character_id="char1", db=fake_session, _user={"id": "u1"})
            return result

        res = self._run_async(_call())
        self.assertTrue(any(o.type == 'in_progress' for o in res.options))
        opt = next(o for o in res.options if o.type == 'in_progress')
        self.assertIn('progress', opt.dialogue)


if __name__ == '__main__':
    unittest.main()

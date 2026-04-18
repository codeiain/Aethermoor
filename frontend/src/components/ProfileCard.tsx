import React, { useState, useEffect } from 'react';

interface PlayerProfile {
  character_id: string;
  name: string;
  level?: number;
  class?: string;
  guild?: string;
  online?: boolean;
}

interface ProfileCardProps {
  targetPlayerId: string;
  onClose: () => void;
  onWhisper?: (playerName: string) => void;
  onPartyInvite?: (playerId: string) => void;
  onFriendAdd?: (playerName: string) => void;
  onBlock?: (playerName: string) => void;
}

export function ProfileCard({
  targetPlayerId,
  onClose,
  onWhisper,
  onPartyInvite,
  onFriendAdd,
  onBlock,
}: ProfileCardProps) {
  const [profile, setProfile] = useState<PlayerProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isBlocked] = useState(false);

  useEffect(() => {
    loadProfile();
  }, [targetPlayerId]);

  async function loadProfile() {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('service_token');
      const [profileRes, statusRes] = await Promise.all([
        fetch(`/api/character/${targetPlayerId}`, {
          headers: { 'X-Service-Token': token || '' },
        }),
        fetch(`/api/social/status/${targetPlayerId}`, {
          headers: { 'X-Service-Token': token || '' },
        }),
      ]);
      if (!profileRes.ok) throw new Error('Player not found');
      const profileData = await profileRes.json();
      let onlineStatus = false;
      if (statusRes.ok) {
        const statusData = await statusRes.json();
        onlineStatus = statusData.online || false;
      }
      setProfile({ ...profileData, online: onlineStatus });
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }


  if (loading) {
    return (
      <div style={styles.overlay} onClick={onClose}>
        <div style={styles.card} onClick={e => e.stopPropagation()}>
          <span style={styles.loading}>Loading...</span>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div style={styles.overlay} onClick={onClose}>
        <div style={styles.card} onClick={e => e.stopPropagation()}>
          <div style={styles.error}>{error || 'Player not found'}</div>
          <button style={styles.closeBtn} onClick={onClose}>✕</button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.card} onClick={e => e.stopPropagation()}>
        <button style={styles.closeBtn} onClick={onClose}>✕</button>
        
        <div style={styles.avatar}>
          {profile.name.charAt(0).toUpperCase()}
        </div>
        
        <h2 style={styles.name}>{profile.name}</h2>
        
        <div style={styles.status}>
          <span
            style={{
              ...styles.statusDot,
              backgroundColor: profile.online ? '#4ade80' : '#6b7280',
            }}
          />
          <span style={styles.statusText}>
            {profile.online ? 'Online' : 'Offline'}
          </span>
        </div>
        
        <div style={styles.details}>
          {profile.level && (
            <div style={styles.detailRow}>
              <span style={styles.label}>Level</span>
              <span style={styles.value}>{profile.level}</span>
            </div>
          )}
          {profile.class && (
            <div style={styles.detailRow}>
              <span style={styles.label}>Class</span>
              <span style={styles.value}>{profile.class}</span>
            </div>
          )}
          {profile.guild && (
            <div style={styles.detailRow}>
              <span style={styles.label}>Guild</span>
              <span style={styles.value}>{profile.guild}</span>
            </div>
          )}
        </div>
        
        {!isBlocked && (
          <div style={styles.actions}>
            {onWhisper && (
              <button style={styles.actionBtn} onClick={() => onWhisper(profile.name)}>
                💬 Whisper
              </button>
            )}
            {onPartyInvite && profile.online && (
              <button
                style={styles.actionBtn}
                onClick={() => onPartyInvite(profile.character_id)}
              >
                🎮 Party
              </button>
            )}
            {onFriendAdd && (
              <button style={styles.actionBtn} onClick={() => onFriendAdd(profile.name)}>
                ⭐ Friend
              </button>
            )}
            {onBlock && (
              <button
                style={{ ...styles.actionBtn, ...styles.blockBtn }}
                onClick={() => onBlock(profile.name)}
              >
                🚫 Block
              </button>
            )}
          </div>
        )}
        
        {isBlocked && (
          <div style={styles.blockedNotice}>You have blocked this player</div>
        )}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  card: {
    background: 'linear-gradient(180deg, #1a1a2e 0%, #16162a 100%)',
    border: '3px solid #fbbf24',
    borderRadius: '8px',
    padding: '20px',
    minWidth: '220px',
    position: 'relative',
    fontFamily: "'Press Start 2P', monospace",
  },
  closeBtn: {
    position: 'absolute',
    top: '8px',
    right: '8px',
    background: 'transparent',
    border: 'none',
    color: '#9ca3af',
    cursor: 'pointer',
    fontSize: '12px',
  },
  loading: {
    color: '#9ca3af',
    fontSize: '10px',
  },
  error: {
    color: '#ef4444',
    fontSize: '10px',
  },
  avatar: {
    width: '64px',
    height: '64px',
    background: 'linear-gradient(180deg, #fbbf24 0%, #d97706 100%)',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 12px',
    fontSize: '24px',
    color: '#1a1a2e',
  },
  name: {
    margin: '0 0 8px 0',
    color: '#fbbf24',
    fontSize: '14px',
    textAlign: 'center',
  },
  status: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px',
    marginBottom: '16px',
  },
  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
  },
  statusText: {
    color: '#9ca3af',
    fontSize: '8px',
  },
  details: {
    borderTop: '1px solid #2a2a3a',
    paddingTop: '12px',
    marginBottom: '16px',
  },
  detailRow: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '8px',
  },
  label: {
    color: '#6b7280',
    fontSize: '8px',
  },
  value: {
    color: '#e5e7eb',
    fontSize: '8px',
  },
  actions: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    justifyContent: 'center',
  },
  actionBtn: {
    background: 'rgba(251, 191, 36, 0.1)',
    border: '1px solid #fbbf24',
    borderRadius: '4px',
    color: '#fbbf24',
    cursor: 'pointer',
    padding: '8px 12px',
    fontSize: '8px',
    fontFamily: "'Press Start 2P', monospace",
  },
  blockBtn: {
    borderColor: '#ef4444',
    color: '#ef4444',
    background: 'rgba(239, 68, 68, 0.1)',
  },
  blockedNotice: {
    color: '#ef4444',
    fontSize: '8px',
    textAlign: 'center',
  },
};
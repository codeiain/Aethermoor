import React, { useState, useEffect } from 'react';

interface Friend {
  character_id: string;
  name: string;
  online: boolean;
}

interface FriendsListProps {
  characterId: string;
  onPartyInvite?: (friendId: string) => void;
  onWhisper?: (friendName: string) => void;
}

export function FriendsList({ characterId, onPartyInvite, onWhisper }: FriendsListProps) {
  const [friends, setFriends] = useState<Friend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadFriends();
  }, [characterId]);

  async function loadFriends() {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('service_token');
      const response = await fetch(`/api/friends/${characterId}`, {
        headers: {
          'X-Service-Token': token || '',
        },
      });
      if (!response.ok) throw new Error('Failed to load friends');
      const data = await response.json();
      setFriends(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  async function removeFriend(friendId: string) {
    try {
      const token = localStorage.getItem('service_token');
      const response = await fetch(`/api/friends/${characterId}/${friendId}`, {
        method: 'DELETE',
        headers: {
          'X-Service-Token': token || '',
        },
      });
      if (!response.ok) throw new Error('Failed to remove friend');
      setFriends(friends.filter(f => f.character_id !== friendId));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    }
  }

  if (loading) {
    return (
      <div className="friends-list-loading" style={styles.container}>
        <span style={styles.loading}>Loading friends...</span>
      </div>
    );
  }

  return (
    <div className="friends-list" style={styles.container}>
      <h3 style={styles.header}>Friends</h3>
      {error && <div style={styles.error}>{error}</div>}
      {friends.length === 0 ? (
        <div style={styles.empty}>No friends yet</div>
      ) : (
        <ul style={styles.list}>
          {friends.map(friend => (
            <li key={friend.character_id} style={styles.listItem}>
              <span style={styles.friendInfo}>
                <span
                  style={{
                    ...styles.statusDot,
                    backgroundColor: friend.online ? '#4ade80' : '#6b7280',
                  }}
                />
                <span style={styles.friendName}>{friend.name}</span>
              </span>
              <span style={styles.actions}>
                {onWhisper && (
                  <button
                    style={styles.actionBtn}
                    onClick={() => onWhisper(friend.name)}
                    title="Whisper"
                  >
                    💬
                  </button>
                )}
                {onPartyInvite && friend.online && (
                  <button
                    style={styles.actionBtn}
                    onClick={() => onPartyInvite(friend.character_id)}
                    title="Invite to Party"
                  >
                    🎮
                  </button>
                )}
                <button
                  style={styles.actionBtn}
                  onClick={() => removeFriend(friend.character_id)}
                  title="Remove Friend"
                >
                  ✕
                </button>
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    background: 'rgba(20, 20, 30, 0.95)',
    border: '2px solid #4a4a5a',
    borderRadius: '4px',
    padding: '8px',
    minWidth: '180px',
    fontFamily: "'Press Start 2P', monospace",
    fontSize: '8px',
  },
  header: {
    margin: '0 0 8px 0',
    color: '#fbbf24',
    fontSize: '10px',
    textAlign: 'center',
  },
  loading: {
    color: '#9ca3af',
  },
  error: {
    color: '#ef4444',
    marginBottom: '8px',
  },
  empty: {
    color: '#6b7280',
    textAlign: 'center',
  },
  list: {
    listStyle: 'none',
    margin: 0,
    padding: 0,
  },
  listItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '4px 0',
    borderBottom: '1px solid #2a2a3a',
  },
  friendInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
  },
  friendName: {
    color: '#e5e7eb',
  },
  actions: {
    display: 'flex',
    gap: '4px',
  },
  actionBtn: {
    background: 'transparent',
    border: '1px solid #4a4a5a',
    borderRadius: '2px',
    color: '#9ca3af',
    cursor: 'pointer',
    padding: '2px 4px',
    fontSize: '8px',
  },
};
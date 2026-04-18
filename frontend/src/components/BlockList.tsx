import React, { useState, useEffect } from 'react';

interface BlockedPlayer {
  character_id: string;
  name: string;
}

interface BlockListProps {
  characterId: string;
}

export function BlockList({ characterId }: BlockListProps) {
  const [blocked, setBlocked] = useState<BlockedPlayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadBlocked();
  }, [characterId]);

  async function loadBlocked() {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('service_token');
      const response = await fetch(`/api/block/${characterId}`, {
        headers: {
          'X-Service-Token': token || '',
        },
      });
      if (!response.ok) throw new Error('Failed to load block list');
      const data = await response.json();
      setBlocked(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  async function unblockPlayer(blockedId: string) {
    try {
      const token = localStorage.getItem('service_token');
      const response = await fetch(`/api/block/${characterId}/${blockedId}`, {
        method: 'DELETE',
        headers: {
          'X-Service-Token': token || '',
        },
      });
      if (!response.ok) throw new Error('Failed to unblock player');
      setBlocked(blocked.filter(b => b.character_id !== blockedId));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    }
  }

  if (loading) {
    return (
      <div className="block-list-loading" style={styles.container}>
        <span style={styles.loading}>Loading block list...</span>
      </div>
    );
  }

  return (
    <div className="block-list" style={styles.container}>
      <h3 style={styles.header}>Blocked</h3>
      {error && <div style={styles.error}>{error}</div>}
      {blocked.length === 0 ? (
        <div style={styles.empty}>No blocked players</div>
      ) : (
        <ul style={styles.list}>
          {blocked.map(player => (
            <li key={player.character_id} style={styles.listItem}>
              <span style={styles.playerName}>{player.name}</span>
              <button
                style={styles.unblockBtn}
                onClick={() => unblockPlayer(player.character_id)}
                title="Unblock"
              >
                ✕
              </button>
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
    color: '#ef4444',
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
  playerName: {
    color: '#e5e7eb',
  },
  unblockBtn: {
    background: 'transparent',
    border: '1px solid #ef4444',
    borderRadius: '2px',
    color: '#ef4444',
    cursor: 'pointer',
    padding: '2px 4px',
    fontSize: '8px',
  },
};
import { useState } from "react";
import { login, register, getMe, ApiError } from "../api/client";
import { useGameStore } from "../store/useGameStore";

const S = {
  wrap: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    height: "100%",
    background: "linear-gradient(180deg, #0d0d2b 0%, #1a0a2e 100%)",
    gap: 24,
    padding: 24,
  },
  title: { fontSize: 32, color: "#c8a84b", textShadow: "0 0 12px #c8a84b88", lineHeight: 1.6 },
  subtitle: { fontSize: 16, color: "#8899aa", marginTop: -12 },
  card: {
    background: "#12182a",
    border: "2px solid #3a4a6b",
    borderRadius: 4,
    padding: 28,
    display: "flex",
    flexDirection: "column" as const,
    gap: 14,
    width: "100%",
    maxWidth: 360,
  },
  tabs: { display: "flex", gap: 8 },
  tab: (active: boolean) => ({
    flex: 1,
    padding: "12px 0",
    fontSize: 14,
    background: active ? "#2a3a5a" : "transparent",
    border: `2px solid ${active ? "#5a7aaa" : "#2a3a4a"}`,
    color: active ? "#e8e0d0" : "#556677",
    cursor: "pointer" as const,
    borderRadius: 2,
  }),
  label: { fontSize: 12, color: "#8899aa", marginBottom: 4 },
  input: {
    background: "#0d1220",
    border: "2px solid #2a3a5a",
    borderRadius: 2,
    color: "#e8e0d0",
    fontSize: 16,
    fontFamily: "inherit",
    padding: "14px 16px",
    width: "100%",
    outline: "none" as const,
  },
  btn: (disabled: boolean) => ({
    background: disabled ? "#1a2233" : "#2a4a8a",
    border: `2px solid ${disabled ? "#2a3a4a" : "#4a7acc"}`,
    color: disabled ? "#445566" : "#e8e0d0",
    fontSize: 16,
    fontFamily: "inherit",
    padding: "16px 0",
    cursor: disabled ? "not-allowed" as const : "pointer" as const,
    borderRadius: 2,
    width: "100%",
  }),
  error: { fontSize: 14, color: "#dd5555", textAlign: "center" as const },
};

export default function LoginScreen() {
  const loginStore = useGameStore((s) => s.login);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit() {
    setError("");
    setLoading(true);
    try {
      let token: string;
      if (mode === "register") {
        const r = await register(email, password);
        token = r.access_token;
      } else {
        const r = await login(email, password);
        token = r.access_token;
      }
      const me = await getMe(token);
      loginStore(token, me.user_id, me.username);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Network error — is the server running?");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={S.wrap}>
      <div style={S.title}>AETHERMOOR</div>
      <div style={S.subtitle}>A WORLD AWAITS</div>
      <div style={S.card}>
        <div style={S.tabs}>
          <button style={S.tab(mode === "login")} onClick={() => setMode("login")}>
            LOGIN
          </button>
          <button style={S.tab(mode === "register")} onClick={() => setMode("register")}>
            REGISTER
          </button>
        </div>

        <div>
          <div style={S.label}>EMAIL</div>
          <input
            style={S.input}
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="hero@aethermoor.io"
            autoComplete="email"
          />
        </div>

        <div>
          <div style={S.label}>PASSWORD</div>
          <input
            style={S.input}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            onKeyDown={(e) => e.key === "Enter" && !loading && handleSubmit()}
          />
        </div>

        {error && <div style={S.error}>{error}</div>}

        <button style={S.btn(loading)} disabled={loading} onClick={handleSubmit}>
          {loading ? "CONNECTING..." : mode === "login" ? "ENTER WORLD" : "CREATE ACCOUNT"}
        </button>
      </div>
    </div>
  );
}

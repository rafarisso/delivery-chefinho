import { FormEvent, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { loginRequest } from "../services/api";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("rafael@delivery.com");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (isAuthenticated) {
    return <Navigate to="/despesas" replace />;
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await loginRequest(email, password);
      login(response.access_token);
      const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? "/despesas";
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha no login");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ maxWidth: "420px", margin: "4rem auto" }}>
      <h2>Entrar</h2>
      <p>Utilize o ADMIN_TOKEN como senha enquanto o login Supabase não é configurado.</p>
      {error && <div className="alert">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div>
            <label>Email</label>
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </div>
        </div>
        <div className="form-row">
          <div>
            <label>Senha</label>
            <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
          </div>
        </div>
        <button className="button" type="submit" disabled={loading}>
          {loading ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}

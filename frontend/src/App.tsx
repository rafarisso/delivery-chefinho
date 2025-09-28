import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";

import { useAuth } from "./hooks/useAuth";
import Despesas from "./pages/Despesas";
import Fechamento from "./pages/Fechamento";
import Login from "./pages/Login";
import Relatorios from "./pages/Relatorios";
import SettlementDetail from "./pages/SettlementDetail";

function PrivateRoute({ children }: { children: JSX.Element }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}

function Navigation() {
  const { isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    return null;
  }

  return (
    <header style={{ backgroundColor: "#111827", color: "#ffffff", padding: "0.75rem 1.5rem" }}>
      <nav className="container" style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <strong>Delivery Cheffinho - Unidade 2</strong>
        <div style={{ display: "flex", gap: "1rem" }}>
          <Link to="/despesas">Despesas</Link>
          <Link to="/fechamento">Fechamento</Link>
          <Link to="/relatorios">Relatórios</Link>
          <button className="button secondary" onClick={logout}>Sair</button>
        </div>
      </nav>
    </header>
  );
}

export default function App() {
  return (
    <>
      <Navigation />
      <main className="container">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/despesas"
            element={
              <PrivateRoute>
                <Despesas />
              </PrivateRoute>
            }
          />
          <Route
            path="/fechamento"
            element={
              <PrivateRoute>
                <Fechamento />
              </PrivateRoute>
            }
          />
          <Route
            path="/relatorios"
            element={
              <PrivateRoute>
                <Relatorios />
              </PrivateRoute>
            }
          />
          <Route
            path="/relatorios/:id"
            element={
              <PrivateRoute>
                <SettlementDetail />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<Navigate to="/despesas" replace />} />
        </Routes>
      </main>
    </>
  );
}

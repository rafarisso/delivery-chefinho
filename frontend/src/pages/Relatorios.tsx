import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listSettlements, Settlement } from "../services/api";
import { useAuth } from "../hooks/useAuth";

function formatCurrency(value: string) {
  const number = Number(value);
  if (Number.isNaN(number)) return value;
  return number.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export default function Relatorios() {
  const { token } = useAuth();
  const [settlements, setSettlements] = useState<Settlement[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!token) return;
      setLoading(true);
      setError(null);
      try {
        const response = await listSettlements(token);
        setSettlements(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro ao carregar fechamentos");
      } finally {
        setLoading(false);
      }
    };
    void fetchData();
  }, [token]);

  return (
    <div>
      <h1>Relatórios semanais</h1>
      {error && <div className="alert">{error}</div>}
      {loading && <p>Carregando...</p>}
      {!loading && settlements.length === 0 && <p>Nenhum fechamento registrado.</p>}
      {!loading && settlements.length > 0 && (
        <table className="table">
          <thead>
            <tr>
              <th>Semana</th>
              <th>Total</th>
              <th>Rafael</th>
              <th>Guilherme</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {settlements.map((item) => (
              <tr key={item.id}>
                <td>
                  {new Date(item.week_start).toLocaleDateString("pt-BR")} -
                  {" "}
                  {new Date(item.week_end).toLocaleDateString("pt-BR")}
                </td>
                <td>{formatCurrency(item.income_total)}</td>
                <td>{formatCurrency(item.total_rafael)}</td>
                <td>{formatCurrency(item.total_guilherme)}</td>
                <td>
                  <Link to={`/relatorios/${item.id}`}>Detalhes</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

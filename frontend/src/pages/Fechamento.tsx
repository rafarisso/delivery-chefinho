import { FormEvent, useState } from "react";

import { closeWeek, downloadWeeklyCsv, downloadWeeklyPdf, Settlement } from "../services/api";
import WeekPicker from "../components/WeekPicker";
import { useAuth } from "../hooks/useAuth";

function formatCurrency(value: string) {
  const number = Number(value);
  if (Number.isNaN(number)) return value;
  return number.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function currentWednesdayISO() {
  const now = new Date();
  const diff = now.getDay() - 3;
  now.setDate(now.getDate() - diff);
  return now.toISOString().slice(0, 10);
}

export default function Fechamento() {
  const { token } = useAuth();
  const [weekEnd, setWeekEnd] = useState(currentWednesdayISO);
  const [ifoodAmount, setIfoodAmount] = useState("0");
  const [ninety9Amount, setNinety9Amount] = useState("0");
  const [rentFee, setRentFee] = useState("50");
  const [rule, setRule] = useState<"rent_before_split" | "rent_after_split">("rent_before_split");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Settlement | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const settlement = await closeWeek(token, {
        week_end: weekEnd,
        ifood_amount: Number(ifoodAmount),
        ninety9_amount: Number(ninety9Amount),
        rent_fee: Number(rentFee),
        rule,
      });
      setResult(settlement);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao fechar semana");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (type: "csv" | "pdf") => {
    if (!token || !result) return;
    try {
      const blob =
        type === "csv"
          ? await downloadWeeklyCsv(token, result.week_end)
          : await downloadWeeklyPdf(token, result.week_end);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `relatorio-${result.week_end}.${type}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao baixar relatório");
    }
  };

  return (
    <div>
      <h1>Fechamento semanal</h1>

      <section className="card">
        <h2>Fechar semana</h2>
        {error && <div className="alert">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <WeekPicker value={weekEnd} onChange={setWeekEnd} />
          </div>
          <div className="form-row">
            <div>
              <label>Recebido iFood</label>
              <input type="number" step="0.01" min="0" value={ifoodAmount} onChange={(event) => setIfoodAmount(event.target.value)} />
            </div>
            <div>
              <label>Recebido 99 Food</label>
              <input type="number" step="0.01" min="0" value={ninety9Amount} onChange={(event) => setNinety9Amount(event.target.value)} />
            </div>
            <div>
              <label>Aluguel (R$)</label>
              <input type="number" step="0.01" min="0" value={rentFee} onChange={(event) => setRentFee(event.target.value)} />
            </div>
          </div>
          <div className="form-row">
            <div>
              <label>Regra</label>
              <select value={rule} onChange={(event) => setRule(event.target.value as typeof rule)}>
                <option value="rent_before_split">Aluguel antes da divisão</option>
                <option value="rent_after_split">Aluguel após a divisão</option>
              </select>
            </div>
          </div>
          <button className="button" type="submit" disabled={loading}>
            {loading ? "Calculando..." : "Fechar semana"}
          </button>
        </form>
      </section>

      {result && (
        <section className="card">
          <h2>Resumo</h2>
          <div className="form-row">
            <div>
              <strong>Período</strong>
              <p>
                {new Date(result.week_start).toLocaleDateString("pt-BR")}
                {" "}- {new Date(result.week_end).toLocaleDateString("pt-BR")}
              </p>
            </div>
            <div>
              <strong>Total recebido</strong>
              <p>{formatCurrency(result.income_total)}</p>
            </div>
            <div>
              <strong>Aluguel</strong>
              <p>{formatCurrency(result.rent_fee)}</p>
            </div>
          </div>
          <div className="form-row">
            <div>
              <strong>Total Rafael</strong>
              <p>{formatCurrency(result.total_rafael)}</p>
            </div>
            <div>
              <strong>Total Guilherme</strong>
              <p>{formatCurrency(result.total_guilherme)}</p>
            </div>
          </div>
          <div className="form-row">
            <div>
              <strong>Despesas Rafael</strong>
              <p>{formatCurrency(result.reimb_rafael)}</p>
            </div>
            <div>
              <strong>Despesas Guilherme</strong>
              <p>{formatCurrency(result.reimb_guilherme)}</p>
            </div>
            <div>
              <strong>Saldo para dividir</strong>
              <p>{formatCurrency(result.net_for_split)}</p>
            </div>
          </div>
          <div style={{ display: "flex", gap: "1rem" }}>
            <button className="button" type="button" onClick={() => handleDownload("csv")}>
              Exportar CSV
            </button>
            <button className="button secondary" type="button" onClick={() => handleDownload("pdf")}>
              Exportar PDF
            </button>
          </div>
        </section>
      )}
    </div>
  );
}

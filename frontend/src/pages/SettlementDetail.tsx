import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { downloadWeeklyCsv, downloadWeeklyPdf, fetchSettlement, Settlement } from "../services/api";
import { useAuth } from "../hooks/useAuth";

function formatCurrency(value: string) {
  const number = Number(value);
  if (Number.isNaN(number)) return value;
  return number.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export default function SettlementDetail() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const [settlement, setSettlement] = useState<Settlement | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!token || !id) return;
      try {
        const response = await fetchSettlement(token, Number(id));
        setSettlement(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro ao carregar fechamento");
      }
    };
    void fetchData();
  }, [id, token]);

  const handleDownload = async (type: "csv" | "pdf") => {
    if (!token || !settlement) return;
    try {
      const blob =
        type === "csv"
          ? await downloadWeeklyCsv(token, settlement.week_end)
          : await downloadWeeklyPdf(token, settlement.week_end);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `relatorio-${settlement.week_end}.${type}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao baixar arquivo");
    }
  };

  if (error) {
    return <div className="alert">{error}</div>;
  }

  if (!settlement) {
    return <p>Carregando...</p>;
  }

  return (
    <section className="card">
      <h2>Fechamento {new Date(settlement.week_end).toLocaleDateString("pt-BR")}</h2>
      <div className="form-row">
        <div>
          <strong>Período</strong>
          <p>
            {new Date(settlement.week_start).toLocaleDateString("pt-BR")} - {" "}
            {new Date(settlement.week_end).toLocaleDateString("pt-BR")}
          </p>
        </div>
        <div>
          <strong>Receita total</strong>
          <p>{formatCurrency(settlement.income_total)}</p>
        </div>
        <div>
          <strong>Aluguel</strong>
          <p>{formatCurrency(settlement.rent_fee)}</p>
        </div>
      </div>
      <div className="form-row">
        <div>
          <strong>Rafael</strong>
          <p>
            Total: {formatCurrency(settlement.total_rafael)}
            <br />
            Reembolso: {formatCurrency(settlement.reimb_rafael)}
            <br />
            Parte: {formatCurrency(settlement.share_rafael)}
          </p>
        </div>
        <div>
          <strong>Guilherme</strong>
          <p>
            Total: {formatCurrency(settlement.total_guilherme)}
            <br />
            Reembolso: {formatCurrency(settlement.reimb_guilherme)}
            <br />
            Parte: {formatCurrency(settlement.share_guilherme)}
          </p>
        </div>
        <div>
          <strong>Saldo</strong>
          <p>{formatCurrency(settlement.net_for_split)}</p>
        </div>
      </div>
      <div style={{ display: "flex", gap: "1rem" }}>
        <button className="button" type="button" onClick={() => handleDownload("csv")}>
          Baixar CSV
        </button>
        <button className="button secondary" type="button" onClick={() => handleDownload("pdf")}>
          Baixar PDF
        </button>
      </div>
    </section>
  );
}

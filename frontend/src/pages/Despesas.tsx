import { FormEvent, useEffect, useMemo, useState } from "react";

import { createExpenseRequest, Expense, listExpenses } from "../services/api";
import FileUpload from "../components/FileUpload";
import { useAuth } from "../hooks/useAuth";

function formatCurrency(value: string) {
  const number = Number(value);
  if (Number.isNaN(number)) {
    return value;
  }
  return number.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export default function Despesas() {
  const { token } = useAuth();
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [amount, setAmount] = useState("");
  const [dateValue, setDateValue] = useState(() => new Date().toISOString().slice(0, 10));
  const [partnerName, setPartnerName] = useState<"Rafael" | "Guilherme">("Rafael");
  const [platform, setPlatform] = useState("");
  const [category, setCategory] = useState("");
  const [note, setNote] = useState("");
  const [receiptFile, setReceiptFile] = useState<File | null>(null);
  const [uploadKey, setUploadKey] = useState(0);

  const [start, setStart] = useState<string>("");
  const [end, setEnd] = useState<string>("");
  const [partnerFilter, setPartnerFilter] = useState<string>("");

  const isFormValid = useMemo(() => amount && dateValue && receiptFile, [amount, dateValue, receiptFile]);

  const fetchExpenses = async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const response = await listExpenses(token, {
        start: start || undefined,
        end: end || undefined,
        partner_name: partnerFilter || undefined,
      });
      setExpenses(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível carregar as despesas");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchExpenses();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token || !receiptFile) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const created = await createExpenseRequest(token, {
        amount: Number(amount),
        date: dateValue,
        partner_name: partnerName,
        platform: platform || undefined,
        category: category || undefined,
        note: note || undefined,
        file: receiptFile,
      });
      setExpenses((previous) => [created, ...previous]);
      setSuccess("Despesa cadastrada com sucesso!");
      setAmount("");
      setNote("");
      setPlatform("");
      setCategory("");
      setReceiptFile(null);
      setUploadKey((prev) => prev + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao salvar a despesa");
    } finally {
      setLoading(false);
    }
  };

  const handleFilter = (event: FormEvent) => {
    event.preventDefault();
    void fetchExpenses();
  };

  return (
    <div>
      <h1>Controle de Despesas</h1>

      <section className="card">
        <h2>Nova despesa</h2>
        {error && <div className="alert">{error}</div>}
        {success && <div className="alert success">{success}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div>
              <label>Valor (R$)</label>
              <input type="number" step="0.01" min="0" value={amount} onChange={(event) => setAmount(event.target.value)} required />
            </div>
            <div>
              <label>Data</label>
              <input type="date" value={dateValue} onChange={(event) => setDateValue(event.target.value)} required />
            </div>
            <div>
              <label>Quem pagou</label>
              <select value={partnerName} onChange={(event) => setPartnerName(event.target.value as "Rafael" | "Guilherme")}> 
                <option value="Rafael">Rafael</option>
                <option value="Guilherme">Guilherme</option>
              </select>
            </div>
          </div>
          <div className="form-row">
            <div>
              <label>Plataforma / Fornecedor</label>
              <input value={platform} onChange={(event) => setPlatform(event.target.value)} placeholder="iFood, 99Food, mercado..." />
            </div>
            <div>
              <label>Categoria</label>
              <input value={category} onChange={(event) => setCategory(event.target.value)} placeholder="ingredientes, embalagem..." />
            </div>
          </div>
          <div className="form-row">
            <div>
              <label>Observação</label>
              <textarea value={note} onChange={(event) => setNote(event.target.value)} rows={3} />
            </div>
          </div>
          <FileUpload key={uploadKey} onFileSelect={setReceiptFile} />
          <button className="button" type="submit" disabled={!isFormValid || loading}>
            {loading ? "Enviando..." : "Salvar despesa"}
          </button>
        </form>
      </section>

      <section className="card">
        <h2>Despesas recentes</h2>
        <form onSubmit={handleFilter} style={{ marginBottom: "1rem" }}>
          <div className="form-row">
            <div>
              <label>Data inicial</label>
              <input type="date" value={start} onChange={(event) => setStart(event.target.value)} />
            </div>
            <div>
              <label>Data final</label>
              <input type="date" value={end} onChange={(event) => setEnd(event.target.value)} />
            </div>
            <div>
              <label>Quem pagou</label>
              <select value={partnerFilter} onChange={(event) => setPartnerFilter(event.target.value)}>
                <option value="">Todos</option>
                <option value="Rafael">Rafael</option>
                <option value="Guilherme">Guilherme</option>
              </select>
            </div>
          </div>
          <button className="button secondary" type="submit">
            Filtrar
          </button>
        </form>

        {loading && <p>Carregando...</p>}
        {!loading && expenses.length === 0 && <p>Nenhuma despesa encontrada.</p>}
        {!loading && expenses.length > 0 && (
          <table className="table">
            <thead>
              <tr>
                <th>Data</th>
                <th>Pagador</th>
                <th>Valor</th>
                <th>Plataforma</th>
                <th>Categoria</th>
                <th>Observação</th>
                <th>Comprovante</th>
              </tr>
            </thead>
            <tbody>
              {expenses.map((expense) => (
                <tr key={expense.id}>
                  <td>{new Date(expense.date).toLocaleDateString("pt-BR")}</td>
                  <td>{expense.partner_name}</td>
                  <td>{formatCurrency(expense.amount)}</td>
                  <td>{expense.platform ?? "-"}</td>
                  <td>{expense.category ?? "-"}</td>
                  <td>{expense.note ?? "-"}</td>
                  <td>
                    {expense.receipt_url ? (
                      <a href={expense.receipt_url} target="_blank" rel="noreferrer">
                        ver nota
                      </a>
                    ) : (
                      "-"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}

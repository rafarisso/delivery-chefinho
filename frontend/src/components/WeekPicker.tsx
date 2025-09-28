import dayjs from "dayjs";
import type { ChangeEvent } from "react";

interface WeekPickerProps {
  value: string;
  onChange: (date: string) => void;
}

const WEDNESDAY = 3;

function ensureWednesday(date: dayjs.Dayjs) {
  const diff = date.day() - WEDNESDAY;
  return date.subtract(diff, "day");
}

function format(date: dayjs.Dayjs) {
  return ensureWednesday(date).format("YYYY-MM-DD");
}

export default function WeekPicker({ value, onChange }: WeekPickerProps) {
  const current = ensureWednesday(dayjs(value));

  const goPrevious = () => {
    onChange(format(current.subtract(7, "day")));
  };

  const goNext = () => {
    onChange(format(current.add(7, "day")));
  };

  const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    const next = dayjs(event.target.value || dayjs());
    onChange(format(next));
  };

  return (
    <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
      <button type="button" className="button secondary" onClick={goPrevious}>
        Semana anterior
      </button>
      <div>
        <label>Quarta-feira</label>
        <input type="date" value={current.format("YYYY-MM-DD")} onChange={handleInputChange} />
      </div>
      <button type="button" className="button secondary" onClick={goNext}>
        Próxima semana
      </button>
    </div>
  );
}

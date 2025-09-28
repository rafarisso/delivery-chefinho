import { useState, ChangeEvent } from "react";

interface FileUploadProps {
  label?: string;
  accept?: string;
  onFileSelect: (file: File | null) => void;
}

export default function FileUpload({ label = "Nota fiscal", accept = "image/*", onFileSelect }: FileUploadProps) {
  const [fileName, setFileName] = useState<string>("");

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setFileName(file ? file.name : "");
    onFileSelect(file ?? null);
  };

  return (
    <div>
      <label>{label}</label>
      <input type="file" accept={accept} onChange={handleChange} />
      {fileName && <small>Selecionado: {fileName}</small>}
    </div>
  );
}

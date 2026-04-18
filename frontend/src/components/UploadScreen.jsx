import { useRef, useState } from "react";

export default function UploadScreen({
  loading,
  error,
  file,
  onFileSelect,
  onUpload,
}) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    const droppedFile = event.dataTransfer.files?.[0] ?? null;
    onFileSelect(droppedFile);
  };

  const handleInputChange = (event) => {
    const chosenFile = event.target.files?.[0] ?? null;
    onFileSelect(chosenFile);
  };

  const handleUploadClick = async () => {
    if (!file) {
      return;
    }

    await onUpload(file);
  };

  return (
    <div className="app-shell screen-fade">
      <div className="card">
        <h1 className="title">Resume Parser</h1>
        <p className="subtitle">
          Upload your resume to extract structured information
        </p>

        <button
          type="button"
          className={`dropzone ${isDragging ? "dropzone-active" : ""}`}
          onClick={() => inputRef.current?.click()}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="dropzone-content">
          <input
            ref={inputRef}
            type="file"
            className="file-input"
            accept=".pdf,.docx"
            onChange={handleInputChange}
          />
          <span className="dropzone-title">Drag and drop your resume here</span>
          <span className="dropzone-text">or click to browse PDF and DOCX files</span>
          {file ? (
            <span className="selected-file">Selected file: {file.name}</span>
          ) : (
            <span className="selected-file">Accepted formats: .pdf, .docx</span>
          )}
          </div>
        </button>

        <button
          type="button"
          className="upload-button"
          disabled={!file || loading}
          onClick={handleUploadClick}
        >
          {loading ? "Uploading..." : "Upload Resume"}
        </button>

        {loading ? (
          <div className="loading-state" role="status" aria-live="polite">
            <span className="spinner" />
            <span>Parsing your resume...</span>
          </div>
        ) : null}

        {error ? <p className="error-text">{error}</p> : null}
      </div>
    </div>
  );
}

import { useEffect, useMemo, useState } from "react";
import { Light as SyntaxHighlighter } from "react-syntax-highlighter";
import json from "react-syntax-highlighter/dist/esm/languages/hljs/json";
import { atomOneDark } from "react-syntax-highlighter/dist/esm/styles/hljs";
import jsPDF from "jspdf";

import "./ResultsView.css";

SyntaxHighlighter.registerLanguage("json", json);

function getDerivedFileType(result, file) {
  if (result?.file_type) {
    return result.file_type;
  }

  const extension = file?.name?.split(".").pop()?.toLowerCase();
  return extension === "pdf" ? "pdf" : "docx";
}

function isParsedResultEmpty(parsedData) {
  return (
    !parsedData?.name &&
    (!parsedData?.email || parsedData.email.length === 0) &&
    (!parsedData?.phone || parsedData.phone.length === 0) &&
    (!parsedData?.skills || parsedData.skills.length === 0)
  );
}

function LoadingSkeleton() {
  return (
    <div className="skeleton-block" aria-hidden="true">
      <span className="skeleton-line skeleton-line-long" />
      <span className="skeleton-line skeleton-line-medium" />
      <span className="skeleton-line skeleton-line-short" />
    </div>
  );
}

export default function ResultsView({ result, file, loading = false, onReset }) {
  const [copied, setCopied] = useState(false);

  const parsedData = result?.parsed ?? {
    name: null,
    email: [],
    phone: [],
    skills: [],
  };

  const fileType = getDerivedFileType(result, file);
  const displayFilename = result?.filename ?? file?.name ?? "resume";
  const formattedJson = useMemo(
    () => JSON.stringify(parsedData, null, 2),
    [parsedData],
  );

  const pdfUrl = useMemo(() => {
    if (!file || fileType !== "pdf") {
      return "";
    }

    return URL.createObjectURL(file);
  }, [file, fileType]);

  useEffect(() => {
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [pdfUrl]);

  useEffect(() => {
    if (!copied) {
      return undefined;
    }

    const timeoutId = window.setTimeout(() => {
      setCopied(false);
    }, 2000);

    return () => window.clearTimeout(timeoutId);
  }, [copied]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(formattedJson);
    setCopied(true);
  };

  const handleDownloadPdf = () => {
    const document = new jsPDF();
    const pageWidth = document.internal.pageSize.getWidth();
    const pageHeight = document.internal.pageSize.getHeight();
    const leftMargin = 20;
    const rightMargin = 20;
    const contentWidth = pageWidth - leftMargin - rightMargin;
    let cursorY = 20;

    const addWrappedText = (text, fontSize = 11) => {
      document.setFontSize(fontSize);
      const lines = document.splitTextToSize(text, contentWidth);

      lines.forEach((line) => {
        if (cursorY > pageHeight - 20) {
          document.addPage();
          cursorY = 20;
        }

        document.text(line, leftMargin, cursorY);
        cursorY += fontSize === 16 ? 10 : 7;
      });
    };

    document.setFont("helvetica", "bold");
    addWrappedText("Parsed Resume Data", 16);

    cursorY += 2;
    document.setFont("helvetica", "normal");
    addWrappedText(`Filename: ${displayFilename}`, 11);

    cursorY += 4;

    const fields = [
      ["Name", parsedData.name || "Not found"],
      [
        "Email",
        parsedData.email?.length ? parsedData.email.join(", ") : "Not found",
      ],
      [
        "Phone",
        parsedData.phone?.length ? parsedData.phone.join(", ") : "Not found",
      ],
      [
        "Skills",
        parsedData.skills?.length ? parsedData.skills.join(", ") : "No skills found",
      ],
    ];

    fields.forEach(([label, value]) => {
      document.setFont("helvetica", "bold");
      addWrappedText(`${label}:`, 11);
      document.setFont("helvetica", "normal");
      addWrappedText(String(value), 11);
      cursorY += 2;
    });

    document.save(`parsed_${displayFilename}.pdf`);
  };

  const showWarningBanner = !loading && isParsedResultEmpty(parsedData);

  return (
    <div className="results-layout screen-fade">
      <section className="results-panel preview-panel">
        <div className="results-panel-header">
          <h2 className="results-heading">Original Resume</h2>
        </div>

        <div className="preview-surface">
          {fileType === "pdf" && pdfUrl ? (
            <iframe
              className="resume-frame"
              src={pdfUrl}
              title="Original resume preview"
            />
          ) : (
            <div className="docx-preview-message">
              DOCX preview not available - parsed data is shown on the right
            </div>
          )}
        </div>
      </section>

      <section className="results-panel parsed-panel">
        <div className="results-panel-header">
          <h2 className="results-heading">Parsed Data</h2>
        </div>

        {showWarningBanner ? (
          <div className="warning-banner">
            Limited data extracted. The resume may be image-based.
          </div>
        ) : null}

        <div className="code-block-wrapper">
          {!loading ? (
            <button className="copy-button" type="button" onClick={handleCopy}>
              {copied ? "Copied!" : "Copy"}
            </button>
          ) : null}

          {loading ? (
            <LoadingSkeleton />
          ) : (
            <SyntaxHighlighter
              language="json"
              style={atomOneDark}
              showLineNumbers={true}
              customStyle={{
                borderRadius: "10px",
                fontSize: "13px",
                maxHeight: "70vh",
                overflowY: "auto",
                margin: 0,
              }}
            >
              {formattedJson}
            </SyntaxHighlighter>
          )}
        </div>

        {!loading ? (
          <div className="results-actions">
            <button
              className="download-button"
              type="button"
              onClick={handleDownloadPdf}
            >
              Download as PDF
            </button>

            <button className="reset-button" type="button" onClick={onReset}>
              Parse Another
            </button>
          </div>
        ) : null}
      </section>
    </div>
  );
}

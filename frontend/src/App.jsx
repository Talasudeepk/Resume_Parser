import "./App.css";

import ResultsView from "./components/ResultsView";
import UploadScreen from "./components/UploadScreen";
import useResumeUpload from "./hooks/useResumeUpload";

function GitHubIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      className="github-icon"
      fill="currentColor"
    >
      <path d="M12 1.5a10.5 10.5 0 0 0-3.32 20.46c.53.1.72-.23.72-.51v-1.8c-2.94.64-3.56-1.24-3.56-1.24-.48-1.22-1.16-1.55-1.16-1.55-.95-.64.07-.62.07-.62 1.05.08 1.61 1.08 1.61 1.08.94 1.6 2.45 1.14 3.05.88.09-.68.37-1.14.66-1.4-2.35-.27-4.82-1.18-4.82-5.23 0-1.15.41-2.09 1.08-2.83-.11-.27-.47-1.36.1-2.82 0 0 .88-.28 2.89 1.08A10 10 0 0 1 12 6.57c.89 0 1.79.12 2.62.35 2-1.36 2.88-1.08 2.88-1.08.57 1.46.21 2.55.1 2.82.68.74 1.08 1.68 1.08 2.83 0 4.06-2.48 4.95-4.84 5.22.38.33.72.97.72 1.96v2.91c0 .28.19.62.73.51A10.5 10.5 0 0 0 12 1.5Z" />
    </svg>
  );
}

function NavigationBar() {
  return (
    <nav className="app-navbar">
      <div className="app-navbar__brand">Resume Parser</div>
      <a
        className="app-navbar__link"
        href="https://github.com"
        target="_blank"
        rel="noreferrer"
        aria-label="View project on GitHub"
      >
        <GitHubIcon />
      </a>
    </nav>
  );
}

export default function App() {
  const {
    loading,
    error,
    result,
    file,
    setFile,
    uploadResume,
    resetResult,
  } = useResumeUpload();

  const showResultsView = Boolean(result) || (loading && file);

  return (
    <div className="app-page">
      <NavigationBar />
      <main className="app-main">
        {showResultsView ? (
          <ResultsView
            result={result}
            file={file}
            loading={loading}
            onReset={resetResult}
          />
        ) : (
          <UploadScreen
            loading={loading}
            error={error}
            file={file}
            onFileSelect={setFile}
            onUpload={uploadResume}
          />
        )}
      </main>
    </div>
  );
}

import { useState } from "react";
import axios from "axios";

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;
const API_BASE_URL = import.meta.env.VITE_API_URL;
const ALLOWED_EXTENSIONS = ["pdf", "docx"];

function getExtension(filename = "") {
  return filename.split(".").pop()?.toLowerCase() ?? "";
}

export default function useResumeUpload() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [file, setFileState] = useState(null);

  const setFile = (nextFile) => {
    if (!nextFile) {
      setFileState(null);
      return;
    }

    const extension = getExtension(nextFile.name);
    if (!ALLOWED_EXTENSIONS.includes(extension)) {
      setFileState(null);
      setError("Only PDF and DOCX files are supported.");
      return;
    }

    if (nextFile.size > MAX_FILE_SIZE_BYTES) {
      setFileState(null);
      setError("File too large. Max size is 10MB.");
      return;
    }

    setFileState(nextFile);
    setError("");
  };

  const uploadResume = async (selectedFile) => {
    if (!selectedFile) {
      setError("Please choose a PDF or DOCX file before uploading.");
      return null;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setResult(response.data);
      return response.data;
    } catch (requestError) {
      if (!requestError.response) {
        setError("Cannot connect to server. Make sure the backend is running.");
        return null;
      }

      const apiCode = requestError.response.data?.code;
      const apiMessage = requestError.response.data?.message;

      if (apiCode === "PARSE_FAILED") {
        setError(
          "We could not extract data from this file. Try a text-based PDF or DOCX.",
        );
      } else {
        setError(apiMessage || "Unable to parse resume right now.");
      }

      return null;
    } finally {
      setLoading(false);
    }
  };

  const resetResult = () => {
    setResult(null);
    setFileState(null);
    setError("");
  };

  return {
    loading,
    error,
    result,
    file,
    setFile,
    uploadResume,
    resetResult,
  };
}

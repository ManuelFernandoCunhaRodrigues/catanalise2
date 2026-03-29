import { useCallback, useEffect, useRef, useState, type ChangeEvent, type DragEvent } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle, FileText, Loader2, Upload } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { analyzeCatDocument } from "@/lib/api";
import { saveLastAnalysis } from "@/lib/analysis-store";
import { toast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type UploadState = "idle" | "uploaded" | "processing" | "done";

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;

export default function UploadCAT() {
  const [state, setState] = useState<UploadState>("idle");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const navigate = useNavigate();
  const redirectTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (redirectTimeoutRef.current !== null) {
        window.clearTimeout(redirectTimeoutRef.current);
      }
    };
  }, []);

  const resetSelection = useCallback(() => {
    setSelectedFile(null);
    setState("idle");
  }, []);

  const prepareFile = useCallback(
    (file?: File | null) => {
      if (!file) {
        resetSelection();
        return;
      }

      const isPdfByName = file.name.toLowerCase().endsWith(".pdf");
      const isPdfByMime = !file.type || file.type === "application/pdf";

      if (!isPdfByName || !isPdfByMime) {
        resetSelection();
        toast({
          title: "Arquivo invalido",
          description: "Selecione um arquivo PDF para continuar.",
          variant: "destructive",
        });
        return;
      }

      if (file.size > MAX_FILE_SIZE_BYTES) {
        resetSelection();
        toast({
          title: "Arquivo muito grande",
          description: "O arquivo precisa ter no maximo 10MB.",
          variant: "destructive",
        });
        return;
      }

      setSelectedFile(file);
      setState("uploaded");
    },
    [resetSelection],
  );

  const handleDrop = useCallback(
    (event: DragEvent<HTMLLabelElement>) => {
      event.preventDefault();
      prepareFile(event.dataTransfer.files[0]);
    },
    [prepareFile],
  );

  const handleFileSelect = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      prepareFile(event.target.files?.[0] ?? null);
      event.target.value = "";
    },
    [prepareFile],
  );

  const handleProcess = useCallback(async () => {
    if (!selectedFile) {
      return;
    }

    setState("processing");

    try {
      const analysis = await analyzeCatDocument(selectedFile);
      saveLastAnalysis(analysis);
      setState("done");

      redirectTimeoutRef.current = window.setTimeout(() => {
        navigate("/analise", { state: { analysis } });
      }, 700);
    } catch (error) {
      setState("uploaded");
      toast({
        title: "Falha ao processar",
        description: error instanceof Error ? error.message : "Nao foi possivel analisar o documento.",
        variant: "destructive",
      });
    }
  }, [navigate, selectedFile]);

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Upload de CAT</h2>
        <p className="mt-1 text-sm text-muted-foreground">Envie o PDF da Certidao de Acervo Tecnico para analise</p>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">Enviar Documento</CardTitle>
        </CardHeader>
        <CardContent>
          <AnimatePresence mode="wait">
            {state === "idle" && (
              <motion.div key="dropzone" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <label
                  onDrop={handleDrop}
                  onDragOver={(event) => event.preventDefault()}
                  className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-border p-12 transition-colors hover:border-primary/50 hover:bg-accent/50"
                >
                  <Upload className="mb-3 h-10 w-10 text-muted-foreground" />
                  <p className="text-sm font-medium">Arraste o PDF aqui ou clique para selecionar</p>
                  <p className="mt-1 text-xs text-muted-foreground">Formatos aceitos: PDF (max. 10MB)</p>
                  <input type="file" accept=".pdf,application/pdf" className="hidden" onChange={handleFileSelect} />
                </label>
              </motion.div>
            )}

            {state === "uploaded" && selectedFile && (
              <motion.div
                key="uploaded"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="space-y-4 text-center"
              >
                <div className="flex items-center justify-center gap-3 rounded-lg bg-accent p-4">
                  <FileText className="h-8 w-8 text-accent-foreground" />
                  <div className="text-left">
                    <p className="text-sm font-medium">{selectedFile.name}</p>
                    <p className="text-xs text-muted-foreground">Pronto para processar</p>
                  </div>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <Button onClick={handleProcess} className="w-full">
                    Processar CAT
                  </Button>
                  <Button variant="outline" onClick={resetSelection} className="w-full">
                    Escolher outro arquivo
                  </Button>
                </div>
              </motion.div>
            )}

            {state === "processing" && (
              <motion.div
                key="processing"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center space-y-4 py-12"
              >
                <Loader2 className="h-10 w-10 animate-spin text-primary" />
                <div className="text-center">
                  <p className="text-sm font-medium">Processando CAT...</p>
                  <p className="mt-1 text-xs text-muted-foreground">Enviando para o backend e registrando a analise</p>
                </div>
                <div className="w-full max-w-xs space-y-2">
                  {["Validando arquivo", "Extraindo conteudo", "Aplicando regras", "Salvando no historico"].map((step, index) => (
                    <motion.div
                      key={step}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.2 }}
                      className="flex items-center gap-2 text-xs text-muted-foreground"
                    >
                      <div className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary" />
                      {step}
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {state === "done" && (
              <motion.div
                key="done"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center space-y-3 py-12"
              >
                <CheckCircle className="h-12 w-12 text-success" />
                <p className="text-sm font-medium">Analise concluida!</p>
                <p className="text-xs text-muted-foreground">Redirecionando para os resultados...</p>
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>
      </Card>
    </div>
  );
}

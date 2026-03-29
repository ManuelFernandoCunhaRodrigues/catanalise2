import { DemoFlow } from "@/components/DemoFlow";


export default function Demo() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Modo Demo</h2>
        <p className="text-muted-foreground text-sm mt-1">
          Uma apresentacao guiada para mostrar upload, analise, risco, score, feedback e historico sem depender de explicacao verbal complexa.
        </p>
      </div>

      <DemoFlow />
    </div>
  );
}

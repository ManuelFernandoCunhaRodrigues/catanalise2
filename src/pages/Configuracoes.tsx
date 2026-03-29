import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";

export default function Configuracoes() {
  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h2 className="text-2xl font-semibold">Configurações</h2>
        <p className="text-muted-foreground text-sm mt-1">Personalize o comportamento do sistema</p>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">Processamento</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="ocr" className="flex flex-col gap-1">
              <span>OCR Automático</span>
              <span className="text-xs text-muted-foreground font-normal">Extrair texto automaticamente ao fazer upload</span>
            </Label>
            <Switch id="ocr" defaultChecked />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <Label htmlFor="ia" className="flex flex-col gap-1">
              <span>Feedback por IA</span>
              <span className="text-xs text-muted-foreground font-normal">Gerar sugestões inteligentes após análise</span>
            </Label>
            <Switch id="ia" defaultChecked />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <Label htmlFor="notif" className="flex flex-col gap-1">
              <span>Notificações</span>
              <span className="text-xs text-muted-foreground font-normal">Receber alertas sobre validações críticas</span>
            </Label>
            <Switch id="notif" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

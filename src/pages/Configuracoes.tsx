import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";

export default function Configuracoes() {
  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Configuracoes</h2>
        <p className="mt-1 text-sm text-muted-foreground">Personalize o comportamento do sistema</p>
      </div>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">Processamento</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="ocr" className="flex flex-col gap-1">
              <span>OCR automatico</span>
              <span className="text-xs font-normal text-muted-foreground">Extrair texto automaticamente ao fazer upload</span>
            </Label>
            <Switch id="ocr" defaultChecked />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <Label htmlFor="ia" className="flex flex-col gap-1">
              <span>Feedback por IA</span>
              <span className="text-xs font-normal text-muted-foreground">Gerar sugestoes inteligentes apos analise</span>
            </Label>
            <Switch id="ia" defaultChecked />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <Label htmlFor="notif" className="flex flex-col gap-1">
              <span>Notificacoes</span>
              <span className="text-xs font-normal text-muted-foreground">Receber alertas sobre validacoes criticas</span>
            </Label>
            <Switch id="notif" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

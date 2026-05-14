import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const endpoints = [
  ["Upload File", "POST", "/files/upload"],
  ["Get Metadata", "GET", "/files/metadata/{upload_id}"],
  ["Allowed Methods", "GET", "/preprocessing/type/{upload_id}"],
  ["Run Clustering", "POST", "/clustering/run"],
  ["Best Clustering", "POST", "/clustering/best"],
  ["Association Mining", "POST", "/association/run"],
  ["Time Series", "POST", "/time-series/run"],
  ["Diagrams", "GET", "/files/diagrams/{upload_id}/{diagram_type}"],
  ["Generate Report", "POST", "/reports/generate"]
];

export default function DocumentationPage() {
  return (
    <AppShell>
      <div className="mx-auto max-w-5xl space-y-8">
        <div>
          <Badge variant="outline">Documentation</Badge>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">API integration map</h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">This frontend reads NEXT_PUBLIC_API_URL and calls the SmartAnalyticsApp API using typed DTOs generated from the provided OpenAPI contract.</p>
        </div>
        <Card className="bg-card/75 backdrop-blur-xl">
          <CardHeader>
            <CardTitle>Workflow</CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="space-y-4 text-sm text-muted-foreground">
              <li><span className="font-semibold text-foreground">1. Upload:</span> send multipart file to /files/upload.</li>
              <li><span className="font-semibold text-foreground">2. Profile:</span> call /preprocessing/type/{'{upload_id}'} to enable compatible algorithm cards.</li>
              <li><span className="font-semibold text-foreground">3. Run:</span> execute algorithm-specific POST endpoints with typed parameters.</li>
              <li><span className="font-semibold text-foreground">4. Visualize:</span> fetch base64 diagrams and render them in lazy galleries with modals.</li>
              <li><span className="font-semibold text-foreground">5. Report:</span> aggregate session results and call /reports/generate.</li>
            </ol>
          </CardContent>
        </Card>
        <Card className="bg-card/75 backdrop-blur-xl">
          <CardHeader>
            <CardTitle>Endpoints</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-hidden rounded-2xl border border-border">
              <table className="w-full text-left text-sm">
                <thead className="bg-muted text-xs uppercase text-muted-foreground">
                  <tr><th className="px-4 py-3">Name</th><th className="px-4 py-3">Method</th><th className="px-4 py-3">Path</th></tr>
                </thead>
                <tbody>
                  {endpoints.map(([name, method, path]) => (
                    <tr key={path} className="border-t border-border">
                      <td className="px-4 py-3 font-medium">{name}</td>
                      <td className="px-4 py-3"><Badge variant={method === "GET" ? "secondary" : "success"}>{method}</Badge></td>
                      <td className="px-4 py-3 font-mono text-muted-foreground">{path}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}

import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'WorkflowOps AI',
  description: 'Governed AI workflow automation platform demo'
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>
}

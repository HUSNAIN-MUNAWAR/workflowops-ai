import './globals.css'
import type { Metadata } from 'next'
import { Manrope, Space_Grotesk } from 'next/font/google'

const sans = Manrope({
  subsets: ['latin'],
  variable: '--font-sans',
})

const display = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-display',
})

export const metadata: Metadata = {
  title: 'WorkflowOps AI',
  description: 'Governed AI workflow automation workspace for approvals, policy-driven execution, reporting, and reliability oversight.'
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en" className={`${sans.variable} ${display.variable}`}><body>{children}</body></html>
}

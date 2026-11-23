import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { PipelinePage } from '@/pages/PipelinePage'
import { DashboardPage } from '@/pages/DashboardPage'
import { PlacesPage } from '@/pages/PlacesPage'
import { SettingsPage } from '@/pages/SettingsPage'
import { Layout } from '@/components/Layout'
import { usePipelineStatus } from '@/hooks/usePipeline'

function App() {
  const { status } = usePipelineStatus()

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/pipeline" element={<PipelinePage />} />
          <Route path="/places" element={<PlacesPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
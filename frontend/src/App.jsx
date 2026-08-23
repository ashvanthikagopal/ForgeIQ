import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { PipelineProvider } from './context/PipelineContext';
import { ThemeProvider } from './context/ThemeContext';
import AppLayout from './components/layout/AppLayout';

import Welcome from './pages/Welcome';
import Dashboard from './pages/Dashboard';
import Pipeline from './pages/Pipeline';
import Products from './pages/Products';
import ProductDetails from './pages/ProductDetails';
import QAReview from './pages/QAReview';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';

import Classification from './pages/Classification';
import Attributes from './pages/Attributes';
import Normalization from './pages/Normalization';
import Descriptions from './pages/Descriptions';
import Enrichment from './pages/Enrichment';

function App() {
  return (
    <ThemeProvider>
      <PipelineProvider>
        <BrowserRouter>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Welcome />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="pipeline" element={<Pipeline />} />
            <Route path="products" element={<Products />} />
            <Route path="products/:id" element={<ProductDetails />} />
            <Route path="qa" element={<QAReview />} />
            <Route path="review" element={<QAReview />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="classification" element={<Classification />} />
            <Route path="attributes" element={<Attributes />} />
            <Route path="normalization" element={<Normalization />} />
            <Route path="descriptions" element={<Descriptions />} />
            <Route path="enrichment" element={<Enrichment />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </PipelineProvider>
  </ThemeProvider>
  );
}

export default App;

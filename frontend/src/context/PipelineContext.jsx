import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { runPipeline, runPipelineWithCSV, getPipelineStatus } from '../services/api';

const PipelineContext = createContext();

export const PipelineProvider = ({ children }) => {
  const [pipelineState, setPipelineState] = useState({
    status: 'idle', // idle, running, completed, failed
    current_stage: 'Part 1',
    part1_count: 0,
    part2_count: 0,
    part3_count: 0,
    part4_count: 0,
    started_at: null,
    completed_at: null,
    error: null,
  });

  const [isRunning, setIsRunning] = useState(false);
  const [backendConnected, setBackendConnected] = useState(true);
  const [toast, setToast] = useState(null); // { message, type: 'info'|'success'|'error' }

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 5000);
  };

  const refreshStatus = useCallback(async () => {
    try {
      const status = await getPipelineStatus();
      setPipelineState(prev => ({ ...prev, ...status }));
      setBackendConnected(true);
      if (status.status === 'running') {
        setIsRunning(true);
      } else {
        setIsRunning(false);
      }
      return status;
    } catch (error) {
      if (error.status === 0) {
        setBackendConnected(false);
      }
      return null;
    }
  }, []);

  const testBackendConnection = useCallback(async () => {
    try {
      await getPipelineStatus();
      setBackendConnected(true);
      showToast('Backend connection verified successfully', 'success');
      return true;
    } catch (error) {
      setBackendConnected(false);
      showToast('Backend offline or unreachable', 'error');
      return false;
    }
  }, []);

  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

  useEffect(() => {
    let intervalId;
    if (isRunning) {
      intervalId = setInterval(refreshStatus, 1000);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isRunning, refreshStatus]);

  const startPipeline = useCallback(async (file = null) => {
    setIsRunning(true);
    showToast(file ? `Starting ForgeIQ enrichment on ${file.name}...` : 'Starting complete ForgeIQ pipeline...', 'info');
    setPipelineState(prev => ({ ...prev, status: 'running', error: null, started_at: new Date().toISOString() }));
    try {
      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        await runPipelineWithCSV(formData);
      } else {
        await runPipeline();
      }
      const finalStatus = await refreshStatus();
      setIsRunning(false);
      const count = finalStatus?.part4_count || 1000;
      showToast(`Pipeline completed successfully! ${count} products processed.`, 'success');
      return finalStatus;
    } catch (error) {
      setPipelineState(prev => ({ ...prev, status: 'failed', error: error.message || error }));
      setIsRunning(false);
      showToast(`Pipeline execution failed: ${error.message}`, 'error');
      throw error;
    }
  }, [refreshStatus]);

  return (
    <PipelineContext.Provider value={{
      pipelineState,
      isRunning,
      backendConnected,
      startPipeline,
      startPipelineWithFile: startPipeline,
      refreshStatus,
      testBackendConnection,
      toast,
      showToast,
      setToast
    }}>
      {children}
    </PipelineContext.Provider>
  );
};

export const usePipeline = () => {
  const context = useContext(PipelineContext);
  if (!context) {
    throw new Error('usePipeline must be used within a PipelineProvider');
  }
  return context;
};

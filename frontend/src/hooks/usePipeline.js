import { usePipeline as usePipelineContext } from '../context/PipelineContext';

export const usePipeline = () => {
  return usePipelineContext();
};

export default usePipeline;

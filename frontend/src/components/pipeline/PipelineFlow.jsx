import React from 'react';
import { PipelineStage } from './PipelineStage';
import { ArrowRight } from 'lucide-react';

export function PipelineFlow({ status, isRunning }) {
  const stages = [
    {
      id: 'part1',
      name: 'PART 1',
      title: 'Foundation',
      responsibilities: ['Load input data', 'Clean input', 'Build lookups', 'Validate input', 'Produce Part1Data'],
      count: status?.part1_count || 0
    },
    {
      id: 'part2',
      name: 'PART 2',
      title: 'Taxonomy & Classification',
      responsibilities: ['Taxonomy classification', 'Attribute extraction', 'Confidence scoring', 'Produce ProductEnrichmentPart2'],
      count: status?.part2_count || 0
    },
    {
      id: 'part3',
      name: 'PART 3',
      title: 'Normalization',
      responsibilities: ['Adapt Part 2 output', 'Normalize mfr & brand', 'Normalize units', 'Build descriptions', 'Produce ProductEnrichmentPart3'],
      count: status?.part3_count || 0
    },
    {
      id: 'part4',
      name: 'PART 4',
      title: 'Enrichment & QA',
      responsibilities: ['Enrich missing attributes', 'Rule validation', 'QA evaluation', 'Package final product catalog'],
      count: status?.part4_count || 0
    }
  ];

  return (
    <div className="flex flex-col xl:flex-row items-stretch justify-between gap-4">
      {stages.map((stage, index) => (
        <React.Fragment key={stage.id}>
          <PipelineStage stage={stage} isRunning={isRunning} currentStage={status?.current_stage} />
          {index < stages.length - 1 && (
            <div className="flex items-center justify-center p-2 xl:py-0">
              <ArrowRight className="h-6 w-6 text-slate-600 hidden xl:block animate-pulse" />
              <ArrowRight className="h-6 w-6 text-slate-600 rotate-90 xl:hidden animate-pulse" />
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

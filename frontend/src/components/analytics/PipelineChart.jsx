import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../common/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function PipelineChart({ part1 = 0, part2 = 0, part3 = 0, part4 = 0 }) {
  const data = [
    { name: 'Part 1', stage: 'Foundation', count: part1 },
    { name: 'Part 2', stage: 'Classification', count: part2 },
    { name: 'Part 3', stage: 'Normalization', count: part3 },
    { name: 'Part 4', stage: 'Enrichment & QA', count: part4 },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Pipeline Stage Counts</CardTitle>
      </CardHeader>
      <CardContent className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc', borderRadius: '8px' }} cursor={{ fill: '#334155', opacity: 0.2 }} />
            <Bar dataKey="count" fill="#4f46e5" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

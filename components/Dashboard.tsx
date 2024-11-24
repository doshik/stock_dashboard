import React, { useState, useEffect, useRef } from 'react';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Bar,
  ComposedChart,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Progress } from "@/components/ui/progress";
import { Clock, Cloud, TrendingUp } from 'lucide-react';
import * as d3 from 'd3';
import cloud from 'd3-cloud';
// Import the JSON data and type it
import dashboardDataJson from '@/data/processed_10k_data_with_names.json';

// Types
interface WordCloudWord {
  text: string;
  value: number;
}

interface WordCloudProps {
  words: WordCloudWord[];
  width?: number;
  height?: number;
}

interface SentimentDataItem {
  type: 'Positive' | 'Negative' | 'Neutral';
  percentage: number;
}

interface TimeSeriesDataItem {
  year: string;
  positivePercent: number;
  negativePercent: number;
  stockPrice: number;
}

interface Company {
  id: string;
  name: string;
}

interface KeyTerms {
  [key: string]: number;
}

interface Metrics {
  sentiment_distribution: {
    positive: number;
    negative: number;
    neutral: number;
  };
  sentiment_percentages: {
    positivePercent: number;
    negativePercent: number;
    neutralPercent: number;
  };
  stockPrice: number;
  key_terms: KeyTerms;
}

interface YearlyMetric {
  company: string;
  year: number;
  metrics: Metrics;
}

interface ProcessedData {
  yearly_metrics: YearlyMetric[];
}

// Type the imported dashboard data
const dashboardData: ProcessedData = dashboardDataJson as ProcessedData;

interface WordCloudWord {
  text: string;
  value: number;
}

interface ProcessedWord extends WordCloudWord {
  size: number;
  x: number;
  y: number;
  rotate: number;
  font: string;
}

interface LayoutWord extends WordCloudWord {
  size: number;
  font: string;
}

interface WordCloudProps {
  words: WordCloudWord[];
  width?: number;
  height?: number;
}

// D3 Word Cloud Component
const D3WordCloud: React.FC<WordCloudProps> = ({
  words,
  width = 600,
  height = 400,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [renderedWords, setRenderedWords] = useState<ProcessedWord[]>([]);

  const fontStack = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';

  useEffect(() => {
    if (!words.length) return;

    // Sort and limit words
    const processedWords = [...words]
      .sort((a, b) => b.value - a.value)
      .slice(0, 100);

    // Calculate size scale
    const fontScale = d3
      .scaleLinear()
      .domain([
        d3.min(processedWords, d => d.value) ?? 0,
        d3.max(processedWords, d => d.value) ?? 1
      ])
      .range([12, 60]);

    // Pre-process words with guaranteed sizes
    const wordsWithSize: LayoutWord[] = processedWords.map(w => ({
      ...w,
      size: fontScale(w.value),
      font: fontStack
    }));

    // Configure the layout
    const layout = cloud<LayoutWord>()
      .size([width, height])
      .words(wordsWithSize)
      .padding(3)
      .rotate(() => 0)
      .spiral("archimedean")
      .font(() => fontStack)
      .fontSize(d => d.size)
      .on("end", (words) => setRenderedWords(words as ProcessedWord[]));

    layout.start();
  }, [words, width, height]);

  const colorScale = d3
    .scaleLinear<string>()
    .domain([0, 1])
    .range(['#60a5fa', '#1d4ed8']);

  const maxValue = d3.max(words, d => d.value) ?? 1;

  return (
    <div className="w-full h-full flex items-center justify-center">
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="overflow-visible"
      >
        <g transform={`translate(${width / 2},${height / 2})`}>
          {renderedWords.map((word, i) => (
            <text
              key={i}
              className="transition-all duration-300 hover:opacity-75 cursor-pointer"
              style={{
                fill: colorScale(word.value / maxValue),
                fontSize: word.size,
                fontFamily: 'Inter',
              }}
              textAnchor="middle"
              transform={`translate(${word.x},${word.y})`}
            >
              <title>{`${word.text}: ${word.value.toFixed(2)}`}</title>
              {word.text}
            </text>
          ))}
        </g>
      </svg>
    </div>
  );
};

// Loading Spinner Component
const LoadingSpinner = () => (
  <div className="min-h-screen bg-gray-50 p-6 flex flex-col items-center justify-center gap-4">
    <Progress value={33} className="w-[60%] mx-auto" />
    <p className="text-gray-600">Loading dashboard data...</p>
  </div>
);

// Main Dashboard Component
const Dashboard: React.FC = () => {
  const [selectedCompany, setSelectedCompany] = useState<string>('');
  const [companies, setCompanies] = useState<Company[]>([]);
  const [sentimentData, setSentimentData] = useState<SentimentDataItem[]>([]);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesDataItem[]>([]);
  const [wordCloudData, setWordCloudData] = useState<WordCloudWord[]>([]);
  const [loading, setLoading] = useState(true);

  // Colors for consistent styling
  const colors = {
    positive: '#22c55e',
    negative: '#ef4444',
    neutral: '#94a3b8',
    stockPrice: '#3b82f6',
  };

  useEffect(() => {
    // Process initial data
    const initializeDashboard = () => {
      try {
        setLoading(true);

        // Get unique companies
        const uniqueCompanies = [
          ...new Set(dashboardData.yearly_metrics.map((item) => item.company)),
        ];
        setCompanies(uniqueCompanies.map((id) => ({ id, name: id })));

        // Set initial selected company
        if (uniqueCompanies.length > 0) {
          setSelectedCompany(uniqueCompanies[0]);
        }
      } catch (error) {
        console.error('Error initializing dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    initializeDashboard();
  }, []);

  useEffect(() => {
    if (!selectedCompany) return;

    // Filter data for selected company
    const companyData = dashboardData.yearly_metrics.filter(
      (item) => item.company === selectedCompany
    );

    // Sort by year
    companyData.sort((a, b) => a.year - b.year);

    // Process sentiment data for pie chart
    const latestYear = companyData[companyData.length - 1];
    if (latestYear) {
      setSentimentData([
        {
          type: 'Positive',
          percentage: latestYear.metrics.sentiment_percentages.positivePercent,
        },
        {
          type: 'Negative',
          percentage: latestYear.metrics.sentiment_percentages.negativePercent,
        },
        {
          type: 'Neutral',
          percentage: latestYear.metrics.sentiment_percentages.neutralPercent,
        },
      ]);

      // Process word cloud data
      const processWordCloudData = (terms: KeyTerms): WordCloudWord[] => {
        return Object.entries(terms)
          .map(
            ([text, value]): WordCloudWord => ({
              text,
              value: value * 100,
            })
          )
          .sort((a, b) => b.value - a.value);
      };

      const wordCloudWords = processWordCloudData(latestYear.metrics.key_terms);
      setWordCloudData(wordCloudWords);
    }

    // Process time series data
    const timeSeries = companyData.map((yearData) => ({
      year: yearData.year.toString(),
      positivePercent:
        yearData.metrics.sentiment_percentages.positivePercent || 0,
      negativePercent:
        yearData.metrics.sentiment_percentages.negativePercent || 0,
      stockPrice: yearData.metrics.stockPrice || 0,
    }));
    setTimeSeriesData(timeSeries);
  }, [selectedCompany]);

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">
            10-K Analysis Dashboard
          </h1>
          <Select value={selectedCompany} onValueChange={setSelectedCompany}>
            <SelectTrigger className="w-72">
              <SelectValue placeholder="Select company" />
            </SelectTrigger>
            <SelectContent>
              {companies.map((company) => (
                <SelectItem key={company.id} value={company.id}>
                  {company.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-12 gap-6">
          {/* Sentiment Distribution Pie Chart */}
          <Card className="col-span-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Sentiment Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex flex-col items-center">
                <div className="h-48 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={sentimentData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        dataKey="percentage"
                        startAngle={90}
                        endAngle={450}
                      >
                        {sentimentData.map((entry) => (
                          <Cell
                            key={entry.type}
                            fill={
                              entry.type === 'Positive'
                                ? colors.positive
                                : entry.type === 'Negative'
                                ? colors.negative
                                : colors.neutral
                            }
                          />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex items-center gap-8 mt-4">
                  {sentimentData.map((entry) => (
                    <div key={entry.type} className="flex items-center gap-2">
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{
                          backgroundColor:
                            entry.type === 'Positive'
                              ? colors.positive
                              : entry.type === 'Negative'
                              ? colors.negative
                              : colors.neutral,
                        }}
                      />
                      <span className="text-sm text-gray-600">
                        {`${entry.type}: ${entry.percentage.toFixed(1)}%`}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Word Cloud */}
          <Card className="col-span-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Cloud className="w-5 h-5" />
                Key Terms Word Cloud
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <D3WordCloud words={wordCloudData} height={256} width={500} />
              </div>
            </CardContent>
          </Card>

          {/* Sentiment Trend with Stock Price */}
          <Card className="col-span-12">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Sentiment Trends and Stock Price
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={timeSeriesData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" interval={0} />
                    <YAxis
                      yAxisId="left"
                      label={{
                        value: 'Sentiment %',
                        angle: -90,
                        position: 'insideLeft',
                      }}
                    />
                    <YAxis
                      yAxisId="right"
                      orientation="right"
                      label={{
                        value: 'Stock Price ($)',
                        angle: 90,
                        position: 'insideRight',
                      }}
                    />
                    <Tooltip />
                    <Bar
                      yAxisId="right"
                      dataKey="stockPrice"
                      fill={colors.stockPrice}
                      opacity={0.3}
                      name="Stock Price"
                    />
                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="positivePercent"
                      stroke={colors.positive}
                      strokeWidth={2}
                      name="Positive %"
                    />
                    <Line
                      yAxisId="left"
                      type="monotone"
                      dataKey="negativePercent"
                      stroke={colors.negative}
                      strokeWidth={2}
                      name="Negative %"
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
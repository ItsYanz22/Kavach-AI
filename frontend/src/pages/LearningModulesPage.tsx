import React, { useState, useEffect } from 'react';
import { useAuth } from '@/auth/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { BookOpen, CheckCircle, RefreshCw } from 'lucide-react';
import { getBackendUrl } from '@/lib/api';
import { useNavigate } from 'react-router-dom';

const API_BASE = getBackendUrl();

interface Module {
  id: string;
  category: string;
  title: string;
  description: string;
  difficulty: string;
  estimated_duration_minutes: number;
  xp_reward: number;
}

interface ModuleProgress {
  module_id: string;
  is_completed: boolean;
  completion_percentage: number;
  quiz_score: number | null;
  times_attempted: number;
}

export const LearningModulesPage: React.FC = () => {
  const [modules, setModules] = useState<Module[]>([]);
  const [progress, setProgress] = useState<Map<string, ModuleProgress>>(new Map());
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<string | null>(null);
  const { getToken, isAuthenticated, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const apiBase = getBackendUrl();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, authLoading, navigate]);

  useEffect(() => {
    const fetchData = async () => {
      if (!isAuthenticated) return;
      
      try {
        const token = getToken();
        if (!token) return;

        // Fetch modules
        const modulesRes = await fetch(`${apiBase}/api/learning/modules`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        
        if (modulesRes.ok) {
          const data = await modulesRes.json();
          // Handle both raw list and ApiResponse envelope
          const modulesData = Array.isArray(data) ? data : data.data || [];
          setModules(modulesData);
        }

        // Fetch progress
        const progressRes = await fetch(`${apiBase}/api/learning/progress`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        
        if (progressRes.ok) {
          const data = await progressRes.json();
          const progressArray = Array.isArray(data) ? data : data.data || [];
          const progressMap = new Map<string, ModuleProgress>(
            progressArray.map((p: ModuleProgress) => [p.module_id, p])
          );
          setProgress(progressMap);
        }
      } catch (error) {
        console.error('Failed to load modules:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [getToken, isAuthenticated, apiBase]);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner':
        return 'bg-green-900 text-green-200';
      case 'intermediate':
        return 'bg-yellow-900 text-yellow-200';
      case 'advanced':
        return 'bg-red-900 text-red-200';
      default:
        return 'bg-slate-700 text-slate-200';
    }
  };

  const categories = Array.from(new Set(modules.filter(m => m.category).map((m) => m.category)));
  const filteredModules = filter ? modules.filter((m) => m.category === filter) : modules;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-emerald-900 to-slate-900 p-4">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-emerald-400 mb-2">📚 Learning Modules</h1>
          <p className="text-slate-400">Master cybersecurity concepts through interactive modules</p>
        </div>

        {/* Filters */}
        <div className="flex gap-2 flex-wrap">
          <Button
            onClick={() => setFilter(null)}
            variant={filter === null ? 'default' : 'outline'}
            className={filter === null ? 'bg-emerald-600' : 'border-slate-600'}
          >
            All Modules ({modules.length})
          </Button>
          {categories.map((category) => (
            <Button
              key={category}
              onClick={() => setFilter(category)}
              variant={filter === category ? 'default' : 'outline'}
              className={filter === category ? 'bg-emerald-600' : 'border-slate-600'}
            >
              {category} ({modules.filter((m) => m.category === category).length})
            </Button>
          ))}
        </div>

        {/* Modules Grid */}
        {isLoading ? (
          <div className="flex justify-center p-8">
            <p className="text-emerald-400">Loading modules...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredModules.map((module) => {
              const moduleProgress = progress.get(module.id);
              const isCompleted = moduleProgress?.is_completed;

              return (
                <Card
                  key={module.id}
                  className={`bg-slate-800/50 border-emerald-500/20 hover:border-emerald-500/50 transition ${
                    isCompleted ? 'opacity-75' : ''
                  }`}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {isCompleted ? (
                          <CheckCircle className="text-emerald-400" size={20} />
                        ) : (
                          <BookOpen className="text-slate-400" size={20} />
                        )}
                        <Badge className={getDifficultyColor(module.difficulty)}>
                          {module.difficulty}
                        </Badge>
                      </div>
                      <Badge variant="outline" className="border-emerald-500 text-emerald-400">
                        +{module.xp_reward} XP
                      </Badge>
                    </div>
                    <CardTitle className="text-lg text-white">{module.title}</CardTitle>
                    <CardDescription className="text-slate-400">{module.description}</CardDescription>
                  </CardHeader>

                  <CardContent className="space-y-4">
                    <div className="text-sm text-slate-400">
                      ⏱️ {module.estimated_duration_minutes} minutes
                    </div>

                    {moduleProgress && (
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-slate-400">Progress:</span>
                          <span className="text-emerald-400">{moduleProgress.completion_percentage}%</span>
                        </div>
                        <div className="w-full bg-slate-700 rounded h-2">
                          <div
                            className="bg-emerald-500 h-2 rounded transition"
                            style={{ width: `${moduleProgress.completion_percentage}%` }}
                          />
                        </div>
                        {moduleProgress.quiz_score !== null && (
                          <p className="text-sm text-slate-400">
                            Quiz Score: <span className="text-emerald-400">{moduleProgress.quiz_score}%</span>
                          </p>
                        )}
                      </div>
                    )}

                    <Button
                      className={`w-full ${
                        isCompleted
                          ? 'bg-slate-700 hover:bg-slate-600'
                          : 'bg-emerald-600 hover:bg-emerald-700'
                      }`}
                      disabled={isCompleted}
                    >
                      {isCompleted ? '✅ Completed' : '📖 Start Learning'}
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
export default LearningModulesPage;

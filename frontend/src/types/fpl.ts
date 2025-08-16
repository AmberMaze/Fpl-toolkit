// FPL API Types
export interface Player {
  id: number;
  name: string;
  team_id: number;
  position: string;
  cost: number;
  total_points: number;
  form: number;
  selected_by_percent: number;
  status: string;
  predicted_points?: number;
}

export interface Team {
  id: number;
  name: string;
  short_name: string;
  strength: number;
}

export interface Projection {
  player_id: number;
  gameweek: number;
  projected_points: number;
  projected_minutes: number;
  confidence_score: number;
  fixture_difficulty: number;
}

export interface TransferScenario {
  player_out_id: number;
  player_in_id: number;
  cost_difference: number;
  points_hit: number;
  expected_return: number;
  risk_score: number;
  recommendation: string;
}

export interface AdvisorRecommendation {
  type: string;
  message: string;
  priority: string;
  confidence_score: number;
  player_ids?: number[];
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
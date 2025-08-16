import { Player, Team, Projection, TransferScenario, AdvisorRecommendation, APIResponse } from '@/types/fpl';

class FPLApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  private async fetchApi<T>(endpoint: string, options?: RequestInit): Promise<APIResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error occurred' 
      };
    }
  }

  // Player endpoints
  async getPlayers(params?: {
    position?: string;
    max_cost?: number;
    min_points?: number;
    limit?: number;
  }): Promise<APIResponse<Player[]>> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const endpoint = `/players${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.fetchApi<Player[]>(endpoint);
  }

  async getPlayer(playerId: number): Promise<APIResponse<Player>> {
    return this.fetchApi<Player>(`/players/${playerId}`);
  }

  async searchPlayers(query: string): Promise<APIResponse<Player[]>> {
    return this.fetchApi<Player[]>(`/players/search?q=${encodeURIComponent(query)}`);
  }

  // Team endpoints
  async getTeams(): Promise<APIResponse<Team[]>> {
    return this.fetchApi<Team[]>('/teams');
  }

  async getTeam(teamId: number): Promise<APIResponse<Team>> {
    return this.fetchApi<Team>(`/teams/${teamId}`);
  }

  async getTeamPlayers(teamId: number): Promise<APIResponse<Player[]>> {
    return this.fetchApi<Player[]>(`/teams/${teamId}/players`);
  }

  // Team-specific endpoints (matching Python backend)
  async getTeamPicks(teamId: number): Promise<APIResponse<any>> {
    return this.fetchApi<any>(`/team/${teamId}/picks`);
  }

  async getTeamAdvisor(teamId: number, params?: {
    budget?: number;
    free_transfers?: number;
    horizon_gameweeks?: number;
  }): Promise<APIResponse<AdvisorRecommendation[]>> {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const endpoint = `/team/${teamId}/advisor${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.fetchApi<AdvisorRecommendation[]>(endpoint);
  }

  async getTeamSummary(teamId: number): Promise<APIResponse<any>> {
    return this.fetchApi<any>(`/team/${teamId}/summary`);
  }

  async getTeamProjections(teamId: number, gameweeks?: number): Promise<APIResponse<Projection[]>> {
    const endpoint = `/team/${teamId}/projections${gameweeks ? `?gameweeks=${gameweeks}` : ''}`;
    return this.fetchApi<Projection[]>(endpoint);
  }

  // Analysis endpoints
  async comparePlayerProjections(playerIds: number[], horizonGameweeks: number = 5): Promise<APIResponse<any>> {
    return this.fetchApi<any>('/compare', {
      method: 'POST',
      body: JSON.stringify({
        player_ids: playerIds,
        horizon_gameweeks: horizonGameweeks,
      }),
    });
  }

  async analyzeTransferScenario(playerOutId: number, playerInId: number): Promise<APIResponse<TransferScenario>> {
    return this.fetchApi<TransferScenario>('/transfer-scenario', {
      method: 'POST',
      body: JSON.stringify({
        player_out_id: playerOutId,
        player_in_id: playerInId,
      }),
    });
  }

  async getPlayerProjections(playerId: number, gameweeks: number = 5): Promise<APIResponse<Projection[]>> {
    return this.fetchApi<Projection[]>(`/players/${playerId}/projections?gameweeks=${gameweeks}`);
  }

  async getFixtureDifficulty(teamId: number, gameweeks: number = 5): Promise<APIResponse<any>> {
    return this.fetchApi<any>(`/teams/${teamId}/fixtures?gameweeks=${gameweeks}`);
  }

  // Fixture endpoints
  async getFixtures(gameweek?: number): Promise<APIResponse<any[]>> {
    const endpoint = gameweek ? `/fixtures?gameweek=${gameweek}` : '/fixtures';
    return this.fetchApi<any[]>(endpoint);
  }

  // Advisor endpoints
  async getAdvice(playerIds: number[], params?: {
    budget?: number;
    free_transfers?: number;
    horizon_gameweeks?: number;
  }): Promise<APIResponse<AdvisorRecommendation[]>> {
    const body = {
      player_ids: playerIds,
      ...params,
    };
    
    return this.fetchApi<AdvisorRecommendation[]>('/advise', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  // Health check
  async healthCheck(): Promise<APIResponse<{ status: string; version: string }>> {
    return this.fetchApi<{ status: string; version: string }>('/');
  }
}

// Export singleton instance
export const fplApi = new FPLApiClient();
export default fplApi;
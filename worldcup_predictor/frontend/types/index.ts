export type Match = { match_id:string; stage:string; group:string; home_team:string; away_team:string; predicted_score:string; winner:string|null; home_win_probability:number; draw_probability:number; away_win_probability:number; decided_by:string };
export type Standing = { team:string; group:string; position:number; played:number; wins:number; draws:number; losses:number; goal_difference:number; points:number; third_place_rank?:number; qualified?:boolean };
export type Odds = { team:string; champion_probability:number; final_probability:number; semifinal_probability:number };

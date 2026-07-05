import os
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Recommendation System Service")

TOP_POPULAR = []
OFFLINE_RECS = {}
SIMILAR_ITEMS = {}

@app.on_event("startup")
def load_data():
    global TOP_POPULAR, OFFLINE_RECS, SIMILAR_ITEMS
    
    if os.path.exists('top_popular.parquet'):
        top_pop_df = pd.read_parquet('top_popular.parquet')
        TOP_POPULAR = top_pop_df['track_id'].tolist()
    else:
        TOP_POPULAR = list(range(100, 120))  
        
    if os.path.exists('recommendations.parquet'):
        recs_df = pd.read_parquet('recommendations.parquet')
        OFFLINE_RECS = recs_df.groupby('user_id')['track_id'].apply(list).to_dict()
        
    if os.path.exists('similar.parquet'):
        sim_df = pd.read_parquet('similar.parquet')
        SIMILAR_ITEMS = sim_df.groupby('track_id')['similar_track_id'].apply(list).to_dict()

class RecommendationRequest(BaseModel):
    user_id: int
    online_history: Optional[List[int]] = None

class RecommendationResponse(BaseModel):
    user_id: int
    recommendations: List[int]
    strategy: str

@app.post("/recommend", response_model=RecommendationResponse)
def get_recommendations(request: RecommendationRequest):
    user_id = request.user_id
    online_history = request.online_history
    
    if user_id in OFFLINE_RECS:
        base_recs = OFFLINE_RECS[user_id].copy()
        strategy = "offline_personal"
    else:
        base_recs = TOP_POPULAR.copy()
        strategy = "fallback_popular"
        
    if online_history and len(online_history) > 0:
        last_track = online_history[-1] 
        
        online_candidates = SIMILAR_ITEMS.get(last_track, [])
        
        if online_candidates:
            mixed_recs = []
            for o, b in zip(online_candidates[:10], base_recs[:10]):
                if o not in mixed_recs: mixed_recs.append(o)
                if b not in mixed_recs: mixed_recs.append(b)
            
            for item in online_candidates + base_recs:
                if len(mixed_recs) >= 20:
                    break
                if item not in mixed_recs:
                    mixed_recs.append(item)
                    
            return RecommendationResponse(
                user_id=user_id,
                recommendations=mixed_recs[:20],
                strategy=f"{strategy}_plus_online"
            )
            
    return RecommendationResponse(
        user_id=user_id,
        recommendations=base_recs[:20],
        strategy=strategy
    )
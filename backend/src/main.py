from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import json
from pathlib import Path

from .embeddings import compare, reset_history
from .state import game

_person_path = Path(__file__).parent.parent / "PERSON.json"
_person_meta = json.loads(_person_path.read_text())

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/person")
def get_person() -> dict:
    return {
        "name": _person_meta["name"],
        "image": _person_meta["image"],
        "hints": _person_meta["hints"],
    }


@app.get("/position")
def get_position() -> dict:
    game.tick()
    return {
        "position": round(game.position, 2),
        "speed": round(game.speed, 2),
        "game_over": game.game_over,
        "won": game.won,
    }


@app.post("/reset")
def reset() -> dict:
    game.reset()
    reset_history()
    return {"position": 0.0, "speed": game.speed}


class InteractRequest(BaseModel):
    text: str


@app.post("/interact")
def interact(req: InteractRequest) -> dict:
    game.tick()
    effect = compare(req.text)

    if isinstance(effect, str):
        return {
            "effect": None,
            "speed": round(game.speed, 2),
            "position": round(game.position, 2),
            "message": "Too similar to a previous prompt.",
        }

    if effect is None:
        message = "No reaction."
    elif effect > 0.5:
        message = "They strongly relate — slowing way down!"
    elif effect > 0.1:
        message = "They relate — slowing down."
    elif effect < -0.5:
        message = "That really upsets them — speeding up fast!"
    elif effect < -0.1:
        message = "That bothers them — speeding up."
    else:
        message = "Mild reaction."

    if effect is not None:
        game.apply_effect(effect)

    return {
        "effect": round(effect, 3) if effect is not None else None,
        "speed": round(game.speed, 2),
        "position": round(game.position, 2),
        "message": message,
    }

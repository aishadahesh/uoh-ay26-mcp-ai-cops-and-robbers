# PRD: GUI And Replay

## Purpose

The GUI provides visual evidence of the multi-agent game and enables user-controlled demonstrations.

## Requirements

- Show the game name and selected play mode.
- Open centered on screen.
- Display legal move targets.
- Support click movement and keyboard movement.
- Support user-vs-agent, user-vs-user, and agent-vs-agent modes.
- Show a start presentation naming the players.
- Show an end presentation naming the winner.
- Save completed games as replay video.
- Include start and end presentation frames in the saved replay.

## Acceptance Criteria

- `New Game` restarts the state.
- `Save Game` is visible.
- `Save Game` only exports completed games.
- Exported replay stops on the final board.
- MP4 export falls back to GIF if needed.

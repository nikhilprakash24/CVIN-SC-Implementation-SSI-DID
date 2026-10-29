# Multi-Image Composition — Process Guide

Source: https://claude.ai/artifact/Nw9gTr9Z3iTE21dMXYLerN (Claude Doc, 2026-10-27, saved 2026-10-28)

## What it is and where it fits

Multi-image composition gives the model several images at once — e.g. your seal, an obstacle, a background and a style example — plus a prompt saying how to combine them. It returns one new image that keeps the identity of each input.

For Flappy Seal it solves the main weakness of plain text-to-image: consistency. Your existing Seal/Otter art becomes a fixed input, so every style test and every world shows the same character. Use it after text-to-image has found candidate styles, to build full scenes from approved pieces.

## Tools to choose from

Input limits and features change often; check each tool's current docs before committing.

| Tool | How it takes multiple images | Best for |
|---|---|---|
| Gemini image models ("Nano Banana") | Several reference images in one chat message | Merging seal + scene + style while keeping identity |
| GPT image (ChatGPT) | Several uploads plus conversational edits | Iterating a composite step by step |
| Midjourney | Separate style reference and character/omni reference slots | Applying a chosen style to your seal |
| Flux Kontext / Flux with IP-Adapter | Image conditioning in local or hosted workflows | Repeatable production pipelines |
| ComfyUI (IP-Adapter + ControlNet) | Any number of references, each with a weight | Full control: pose, style and identity separately |
| Scenario / Leonardo | Trained models plus image guidance | Batch game assets in one locked style |

## Preparing references and writing the prompt

Give each input one job. A reference that does two jobs (e.g. a seal photo with a busy background) confuses the model.

| Input role | What makes a good one | Flappy Seal example |
|---|---|---|
| Character | Clean, plain background, clear silhouette, side view | Seal on white, flippers visible |
| Object | One obstacle, isolated | Fish hook on white |
| Environment | Background with empty space where the action goes | Kelp gap with open water in the middle |
| Style | An image whose look you want, not its content | A painterly reef from your style tests |
| Layout (optional) | A rough sketch of where things sit | Box for seal left, pipes right, arrow for current |

Prompt pattern — name each image by its order and role:

> Image 1 is the character, Image 2 is the background, Image 3 is the style reference. Place the seal from Image 1 swimming upward through the kelp gap in Image 2, with an upward current of bubbles. Render the whole scene in the style of Image 3. Keep the seal's shape, face and colours exactly as in Image 1. Side view, 16:9, clear silhouette.

Tips:

- Say what must stay fixed ("keep the seal exactly") and what may change ("restyle everything").
- Use 2–4 images; more inputs usually weaken each one.
- Match aspect ratios and lighting direction across inputs where you can.

## The professional process

The same brief → diverge → converge → lock → produce loop as text-to-image, but built around a library of approved reference pieces.

1. **Build the reference library.** Collect your existing Seal/Otter art, each cleaned onto a plain background. Add the best style candidates from text-to-image testing. Store each in a folder by role: characters, obstacles, environments, styles.
2. **Make a character sheet.** Generate (or clean up) the seal in 4–6 poses on one plain sheet: front, side, swimming up, diving, hit. This becomes the single character input for everything after.
3. **Define the test scene.** Same scene as text-to-image testing: seal + one obstacle + current + background, so results compare directly.
4. **Diverge: style swap.** Keep the character and environment inputs fixed; swap only the style reference. Generate 4–8 per style.
5. **Check identity.** Put each output next to the character sheet. Reject any where the seal's face, proportions or colours drifted.
6. **Gameplay test.** Shrink to phone size: seal visible at a glance, hazards distinct from scenery, current readable, works in greyscale.
7. **Converge: shortlist 3–4 styles.** Score readability, appeal, uniqueness and feasibility, 1–5 each.
8. **Stress-test across worlds.** For each shortlisted style, compose the seal into 2–3 worlds (deep sea, Antarctica, swamp) and with 2 obstacles (hook, eel). Viable styles stay consistent in all of them.
9. **Get outside eyes.** Show 3–5 people the shortlist without saying which you prefer.
10. **Lock the style.** Write the style guide: palette, line weight, shading, seal proportions, the prompt pattern, and the exact reference images to always attach.
11. **Produce in layers.** Compose assets separately — characters, obstacles, background layers for parallax — rather than one baked scene, so they work in the engine.
12. **Clean up and review in engine.** Remove backgrounds, upscale, fix small errors, unify colours, then judge in motion at real size.

Log every keeper: input images used, prompt, tool, model version, date.

## Common problems and licensing

| Problem | Fix |
|---|---|
| Seal changes shape or face | Use the character sheet as input; state "keep the seal exactly as Image 1"; fewer total inputs |
| Style image's content leaks in (its fish appear in your scene) | Pick a style reference with simpler content, or lower its weight |
| Elements look pasted on | Ask for matching lighting and shadows; use environment inputs with consistent light direction |
| Model ignores one input | Refer to it by number and role in the prompt; drop to 2–3 inputs |
| Lighting or scale mismatch | Describe size relationships ("seal is half the gap height") |
| Background baked into sprite | Compose characters on plain backgrounds; remove the background after |

**Licensing:** only use reference images you own or have rights to — your own art, your own generations, or licensed assets. Check each tool's commercial-use terms for your plan before release.

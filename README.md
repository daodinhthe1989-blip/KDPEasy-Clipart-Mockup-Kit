# KDPEasy Clipart & Mockup Kit

A Streamlit tool that assembles ChatGPT prompts in two steps. No image generation
and no API call inside the tool itself - pure text templating, same model as
Storybook Prompt Kit and Prompt Generator.

## What it does

1. **Step 1 - Shot list.** You enter a theme (or, in "promo bonus" mode, the
   product/niche you're promoting), pick a mode, and the tool builds one prompt
   that asks ChatGPT for a numbered shot list.
2. **Step 2 - Image prompts.** You paste ChatGPT's reply back in. The tool turns
   every line into its own ready-to-run image prompt, with a style lock applied
   consistently across the whole set.

Two modes, same two-step flow:
- **Clipart set** - isolated objects on a transparent or white background. For
  a themed clipart pack to sell, or to use as a bonus.
- **Listing mockup scenes** - the customer uploads a real screenshot or page of
  their own product; each prompt places it into a styled scene (flatlay,
  lifestyle, studio) for an Etsy or TPT listing photo.

The "I'm building this to: Sell as a product / Use as a promo bonus" toggle only
changes the field labels - the generated prompts are identical either way, so
the same tool covers both uses.

## Status

v1 - single access tier, no OTOs yet. The funnel split (a cleanup/upscale pass,
a matching digital-paper generator, a dual Etsy+TPT listing-description helper)
is still being decided; add new entries to the `PASSWORDS` dict in `app.py` the
same way Storybook Prompt Kit does once that's locked.

Password: `KDPCLIPART2026` (change the string in `app.py` before using it for
real - placeholder for now).

## Deploy (GitHub web editor + Streamlit Cloud, no Git CLI)

1. Create a new GitHub repo, e.g. `kdpeasy-clipart-mockup-kit`.
2. Use the GitHub web editor ("Add file" -> "Upload files" or "Create new file")
   to add `app.py`, `requirements.txt`, and `.streamlit/config.toml` from this
   folder.
3. On Streamlit Community Cloud, create a new app pointing at that repo,
   `app.py` as the entry point.
4. Test with the password above before sharing it.

## Known limitation to mention to buyers

ChatGPT's image tool does not always keep an uploaded reference image perfectly
untouched in "mockup scenes" mode - check each result before using it, same
honest caveat already used for Storybook Prompt Kit's text-in-image feature.

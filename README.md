# JFL Manager Mode update

Extract this ZIP into the root of `somebasicgoats/JFL`. Keep the folder paths, including `api/`, `matches/`, `tools/` and `package.json`. Commit the files to `main`. The connected JFL Vercel project builds the update automatically.

Use the current **Other** framework preset and root directory `./`. The included `vercel.json` sets the build command, output directory, and share routes. No environment variable or SQL migration is required. The share function reads the same public Supabase tables as the website.

## Manager Mode

- In Admin, use **Manager Mode roster** to choose who starts new careers. Use the automatic option to include current and future JFL players. Existing careers keep their squads.
- In Manager Mode, use **Column filters** to combine searches across a table. Select any column heading to sort. Use comparisons like `>=70` for ratings and `>=2026-09-01` for dates.
- Open **Talk** in Squad or Training to see a player’s mood, condition, latest match rating and conversation history. Your choices can change morale, sharpness or the player’s training plan. The next conversation is available after seven in-game days.
- Click a position on the lineup pitch to pick or inspect a starter. Select a session in Training to edit drills on the training pitch. Click a player name to open their simulated career profile. Click a recent score in the match centre to open its report.

- New careers let you choose Accessible, Standard or Demanding difficulty. Choose a real JFL season to use its competitive match logs as the rating sample. Custom start dates use the last completed season with match logs, or the preceding 12 months if there is no completed season.
- In Admin, open **Manager Mode ratings** to see the automatic estimate and optionally set talent or potential. Overrides apply when a new career is created. Clear both fields and save to restore automatic ratings. An existing career keeps the attributes it already simulated.
- The Squad screen saves manual lineup picks immediately. Auto covers an injured, suspended or absent player temporarily. **Lock projected XI** can save the visible Auto picks into the remaining slots.
- Season simulation pauses for board decisions and international call-ups. Resolve the prompt after highlights to continue. School league players cannot be called up. New school seasons in new saves start with rivals calibrated to the opening JFL squad. Bankruptcy ends the career and leaves its tables and match reports available until you start a new one.
- Saves are browser storage for the current domain and account.

## Discord previews

After the updated Vercel deployment is ready, use **Copy match link** or **Copy profile link** on the JFL site. The new share URLs include `/share/match/` or `/share/player/` and give Discord the title, description, image and yellow theme color. The preview depends on the new URL, so copy a fresh link when an older link only opens the website.


## Deployment notes

Vercel packages the share endpoint from `api/share.js` as an ES module. The GitHub Pages workflow is independent of the Vercel deployment. If Pages reports that the `github-pages` artifact is missing together with an artifact metadata/API error, rerun that workflow; the deploy step cannot publish until the upload step succeeds.

## Remove the old GitHub Pages workflow

This site now deploys through Vercel. If the repository already has `.github/workflows/match-previews.yml`, delete that file in GitHub and commit the deletion. It schedules GitHub Pages deployments every 30 minutes; those are unnecessary for Vercel and can generate failed-run emails. The Vercel share function handles Discord previews.

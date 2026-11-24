# JFL Manager Mode update

Extract this ZIP into the root of `somebasicgoats/JFL`. Keep the folder paths, including `api/`, `matches/`, `tools/`, `.github/` and `package.json`. Commit the files to `main`. The connected JFL Vercel project builds the update automatically.

Use the current **Other** framework preset and root directory `./`. The included `vercel.json` sets the build command, output directory, and share routes. No environment variable or SQL migration is required. The share function reads the same public Supabase tables as the website.

## Manager Mode

- New careers let you choose Accessible, Standard or Demanding difficulty. Choose a real JFL season to use its competitive match logs as the rating sample. Custom start dates use the last completed season with match logs, or the preceding 12 months if there is no completed season.
- In Admin, open **Manager Mode ratings** to see the automatic estimate and optionally set talent or potential. Overrides apply when a new career is created. Clear both fields and save to restore automatic ratings. An existing career keeps the attributes it already simulated.
- The Squad screen saves manual lineup picks immediately. Auto covers an injured, suspended or absent player temporarily. **Lock projected XI** can save the visible Auto picks into the remaining slots.
- Season simulation stops when a board decision is due. Resolve it in the Inbox to continue. Bankruptcy ends the career and leaves its tables and match reports available until you start a new one.
- Saves are browser storage for the current domain and account.

## Discord previews

After the updated Vercel deployment is ready, use **Copy match link** or **Copy profile link** on the JFL site. The new share URLs include `/share/match/` or `/share/player/` and give Discord the title, description, image and yellow theme color. The preview depends on the new URL, so copy a fresh link when an older link only opens the website.


## Deployment notes

Vercel packages the share endpoint from `api/share.js` as an ES module. The GitHub Pages workflow is independent of the Vercel deployment. If Pages reports that the `github-pages` artifact is missing together with an artifact metadata/API error, rerun that workflow; the deploy step cannot publish until the upload step succeeds.

## Remove the old GitHub Pages workflow

This site now deploys through Vercel. If the repository already has `.github/workflows/match-previews.yml`, delete that file in GitHub and commit the deletion. It schedules GitHub Pages deployments every 30 minutes; those are unnecessary for Vercel and can generate failed-run emails. The Vercel share function handles Discord previews.

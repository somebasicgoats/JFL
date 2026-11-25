JFL KORP — Account Custom Themes (patch bundle)

This ZIP is a PATCH BUNDLE, not a complete deployable website ZIP. It deliberately avoids shipping an older index.html snapshot over your friend's newer GitHub work.

Apply to the current GitHub repository:
1. Check out the latest main branch of somebasicgoats/JFL.
2. Copy apply_custom_themes.py into the repository root (beside index.html).
3. Run: python apply_custom_themes.py
4. Open Supabase SQL Editor and run jfl_user_themes.sql once.
5. Review the diff in index.html, test locally, then commit/deploy through your normal workflow.

What it adds:
- A Custom option in the existing theme selector (expects the current Blue theme option to be present).
- Three native color-wheel controls in Account settings: primary, secondary, tertiary.
- Immediate color preview while editing.
- Save to the signed-in Supabase account; colors load again when that account signs in on another device.
- Row Level Security restricts each account to its own row.

Safety:
- The patch script checks that each expected source anchor occurs exactly once and refuses to write if the current index.html structure differs.
- SQL creates only the jfl_user_themes table and its own RLS policies. It does not alter league data, player profiles, or Manager Mode careers.
- The patch has not been deployed or tested against the live Vercel site. Run the script against the current main checkout and inspect its diff before deployment.

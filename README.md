# fmt_MLB
 A Collection of scripts for professional baseball games released after 2023
 
fmt_MLB_PS4.py
For Noesis. Mostly for static models from #23 on PS4 (Also tested on static models from #24 on Switch).
It can load character models but the bone hierarchy was too confusing.
Some animated character models from #23 on PS4 won't load (They seem to be transplanted from older games so I gave up).
Also won't load blendshapes. The shapes are compressed somehow (Except when they aren't).
Character faces won't work out of the box.
 
tex_MLB_tex.py
For Noesis. I think I got most of the texture formats. I'm not use to working with PS4 and Switch textures tiling nonsense but I think I did all right.
Sure wish Noesis wouldn't rename the first texture in an archive by default. So watch out for that.

MLB_Parse.py
Something I put together to help me figure these things out. Currently good for displaying material information.
 
MLB_LightRigJSONtoUE4.py
The whole reason I started this was because I thought it would be fun to look at the stadiums in UE4.
Unfortunately the games handedness doesn't match UE4. So nothing is rotated the right way. I'm sure there is a way to fix that but whatever.
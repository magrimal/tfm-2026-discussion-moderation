  UI Design Brief: Discussion Moderation UI                                                                                                                                                    
                                                                                                                                                                                              
  Purpose                                                                                                                                                                                     
                                                                                                                                                                                              
  A research dashboard for a master's thesis on AI-driven discussion facilitation. A single researcher uses it locally to compare how different language models behave when analyzing academic
   discussion threads. The primary activity is: run an experiment, open the dashboard, read and compare results.
                                                                                                                                                                                              
  ---             
  Overall layout
                
  Single-page app. Fixed left sidebar for navigation and filters. Main content area on the right changes based on the active view.
                                                                                                                                                                                              
  No header/topbar needed. No authentication. No mobile breakpoints.                                                                                                                          
                                                                                                                                                                                              
  Sidebar (~240px)                                                                                                                                                                            
  - App title: "Discussion Moderation" (small, understated)
  - Run selector: dropdown with run directory names (e.g. "2026-04-26 — all 10 local"). Most recent selected by default.                                                                      
  - View switcher: 4 items (described below)                                                                            
  - Model filter: multi-select checkboxes, one per model in the selected run. All selected by default.                                                                                        
  - Tier filter: 3 toggle pills — Full / Partial / None (from the compatibility tier classification)                                                                                          
                                                                                                                                                                                              
  ---                                                                                                                                                                                         
  View 1: Overview                                                                                                                                                                            
                                                                                                                                                                                              
  Default view when you open the dashboard.
                                                                                                                                                                                              
  Model summary table (full width, one row per model)                                                                                                                                         
                                                                                                                                                                                              
  Columns: Model name, Family, Size, Completion (e.g. "6/6"), Classification accuracy (e.g. "4/6"), Intervene accuracy (e.g. "3/4"), Avg duration, Errors.                                    
                  
  Rows are sorted by completion then classification accuracy descending. Clicking a row navigates to View 3 (per-model detail) for that model.                                                
                  
  Color encoding in cells:                                                                                                                                                                    
  - Completion 6/6: green dot. Less: yellow or red dot.
  - Errors > 0: red badge with error count.                                                                                                                                                   
                                           
  Below the table, a small note: "Classification accuracy = state matches expected thread label. Intervention accuracy = decision matches expected for thread type."                          
                                                                                                                                                                                              
  ---                                                                                                                                                                                         
  View 2: Classification heatmap                                                                                                                                                              
                                
  Grid — rows = models, columns = 6 thread scenarios (new, active, stalled, conflictive, convergent, off_topic). Each cell shows the classified state as a short label.
                                                                                                                                                                                              
  Color coding per cell:
  - Dark green: classified state matches the thread's expected state                                                                                                                          
  - Light yellow: classified a plausible adjacent state (e.g. "new" vs "stalled")
  - Red: clearly wrong or error                                                  
  - Grey: skipped / no data                                                                                                                                                                   
                           
  Thread column headers show both the scenario key and a short title (e.g. "stalled — Open source licensing").                                                                                
                                                                                                                                                                                              
  Hovering a cell shows a popover with:
  - Model + thread                                                                                                                                                                            
  - Classified state, trajectory, participation balance, discourse quality, inquiry phase                                                                                                     
  - Classification reasoning (truncated to ~3 lines, "read more" expands)                
  - Confidence value                                                                                                                                                                          
                                                                                                                                                                                              
  This is the most important view for quick visual pattern recognition across models.                                                                                                         
                                                                                                                                                                                              
  ---             
  View 3: Per-model detail                                                                                                                                                                    
                          
  Top: model name as heading. Stats row: completion, accuracy, avg duration, errors.
                                                                                                                                                                                              
  Thread result cards — one card per thread scenario, arranged in a 2-column grid (3 rows × 2 cols for 6 threads). Each card has:                                                             
                                                                                                                                                                                              
  - Thread title + scenario key as card header (e.g. "conflictive — Regulation of AI in the EU")                                                                                              
  - Classification strip: state label + color dot, trajectory, balance, discourse quality, inquiry phase — displayed as compact pills
  - Intervention decision: large "INTERVENE" (green) or "NO INTERVENTION" (grey) label                                                                                                        
  - If INTERVENE: role pill + technique label + post_to_thread indicator (posted vs instructor-only)                                                                                          
  - Confidence row at the bottom: four small values — c_conf, i_conf, r_conf, resp_conf — shown as decimals with a subtle background bar indicating the value                                 
  - Error state: if error, card gets a red left border and shows the error message                                                                                                            
                                                                                                                                                                                              
  Clicking a card expands it in-place to show:                                                                                                                                                
  - Full classification reasoning                                                                                                                                                             
  - Intervention reasoning                                                                                                                                                                    
  - Role reasoning (if applicable)
  - Response reasoning + response text (the actual message the AI would post, in a distinct text box with a quote-like style)
                                                                                                                                                                                              
  ---                                                                                                                                                                                         
  View 4: Cross-model by thread                                                                                                                                                               
                                                                                                                                                                                              
  Thread selector at the top: 6 tab buttons, one per scenario.
                                                                                                                                                                                              
  Below: a comparison table for the selected thread, one row per model.                                                                                                                       
                                                                                                                                                                                              
  Columns: Model, Classified state (with correctness indicator), Intervene decision, Role (if applicable), Technique (if applicable), c_conf, Duration.                                       
                  
  Below the table: response texts side by side. Each model that generated a response gets a card showing the response text. Cards are same width, scrollable if long. Header of each card =   
  model name.     
                                                                                                                                                                                              
  This view is for the thesis: "for the conflictive thread, here is what each model generated."                                                                                               
   
  ---                                                                                                                                                                                         
  View 5: Confidence
                    
  Per-model confidence strip — for each model, a row of 4 dots (one per confidence field: classification, intervention, role, response). Dot size or fill encodes the value.
                                                                                                                                                                                              
  Below: a small scatter plot. X axis = thread scenario (6 categories). Y axis = confidence value 0–1. One series per confidence type (4 series, color coded). Each point is one model's value
   for that thread.                                                                                                                                                                           
                                                                                                                                                                                              
  Placeholder note at the bottom: "Pedagogical quality scores (LLM-as-judge) will appear here once Capa 2 evaluation is implemented."                                                         
   
  ---                                                                                                                                                                                         
  Visual style    
              
  Tone: academic tool, not a product. Clean, data-forward, no decorative elements.
                                                                                                                                                                                              
  - Background: off-white (#F9F9F7) for the page, white for cards                                                                                                                             
  - Sidebar: light grey (#F0F0EE)                                                                                                                                                             
  - Primary accent: a muted teal or slate blue for interactive elements and "correct" indicators                                                                                              
  - Error/incorrect: muted red (#C0392B equivalent, not neon)                                                                                                                                 
  - Correct: muted green (#27AE60 equivalent)                                                                                                                                                 
  - Typography: a single sans-serif (Inter or equivalent), no display fonts. Mono for model names, state labels, and confidence values.                                                       
  - Card borders: 1px light grey, no shadows or very subtle shadows                                                                                                                           
                                                                                                                                                                                              
  ---                                                                                                                                                                                         
  Key interactions                                                                                                                                                                            
                                                                                                                                                                                              
  - Sidebar model filter → all views update live
  - Run selector → reload all data for that run                                                                                                                                               
  - Clicking a model row in Overview → jump to View 3 for that model
  - Clicking a thread card → expand in place to show reasoning + response text                                                                                                                
  - Hovering a heatmap cell → popover with classification details                                                                                                                             
  - Thread tabs in View 4 → switch thread, preserve model filters                                                                                                                             
                                                                                                                                                                                              
  ---                                                                                                                                                                                         
  What to leave out of the design                                                                                                                                                             
                                                                                                                                                                                              
  - No dark mode
  - No export or download buttons                                                                                                                                                             
  - No settings panel
  - No notifications or status bar
  - No animations beyond basic open/close of expandable cards                                                                                                                                 
                                                                 
\version "2.24.0"
\language "italiano"

% --- DEFINIZIONI GRAFICHE ---

% Freccia Nera (Risoluzioni corrette)
freccia = {
  \override Glissando.style = #'line
  \override Glissando.thickness = #2
  \override Glissando.bound-details.right.arrow = ##t
  \override Glissando.color = #black
}

% Freccia Grigia (Errori/Parallelismi)
frecciag = {
  \override Glissando.style = #'line
  \override Glissando.thickness = #2
  \override Glissando.bound-details.right.arrow = ##t
  \override Glissando.color = #(x11-color 'grey60)
}

% Note di passaggio (piccole)
passaggio = #(define-music-function (music) (ly:music?)
#{ \magnifyMusic 0.6 $music #})

% --- FUNZIONE "PARTILATE" (SATB AUTOMATICO) ---
% Argomenti:
% 1. global (tempo, tonalità)
% 2. soprano (note)
% 3. alto (note)
% 4. tenor (note)
% 5. bass (note)
% 6. analysis (testo/numeri romani)
% 7. figures (basso numerato)

partilate = #(define-music-function 
    (global soprano alto tenor bass analysis figures)
    (ly:music? ly:music? ly:music? ly:music? ly:music? ly:music? ly:music?)
    #{
    \new PianoStaff <<
        \new Staff = "upper" <<
            $global
            \new Voice = "soprano" { \voiceOne $soprano }
            \new Voice = "alto" { \voiceTwo $alto }
        >>
        \new Staff = "lower" <<
            \clef bass
            $global
            \new Voice = "tenor" { \voiceOne $tenor }
            \new Voice = "bass" { \voiceTwo $bass }
        >>
        
        % Analisi (Gradi)
        \new Lyrics \with { alignBelowContext = "lower" } \lyricmode { $analysis }
        
        % Basso Figurato (Numeri)
        \new FiguredBass { 
            % Attiva le linee di estensione automaticamente
            \set FiguredBass.useBassFigureExtenders = ##t
            \figuremode { $figures } 
        }
    >>
    #})

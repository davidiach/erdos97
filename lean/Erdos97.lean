-- Library root: importing every module makes `lake build` compile the
-- whole pilot, which the required Lean CI job builds and then rechecks
-- file-by-file via scripts/check_lean_files.py.
import Erdos97.Basic
import Erdos97.CertificateFormats
import Erdos97.OfficialBridge
import Erdos97.SelectedWitness
import Erdos97.TurnPacking
import Erdos97.TwoCircleCap
import Erdos97.WitnessLemmas
import Erdos97.Sketches.T01SelfEdge
import Erdos97.Sketches.T10StrictCycle
import Erdos97.Sketches.T20TwoCircleCap
import Erdos97.Sketches.T30IncidenceCount
import Erdos97.Sketches.T40N8Certificate

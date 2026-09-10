import Erdos9796Proof.P97.ATail.TwoRadiusGridNestedEscapeTerminal

/-!
Audit the two named conditional terminals, including their transitive axiom
closures. Unlike N9Audit, this does not inline the project geometry vocabulary.
The printed signatures and the pinned sources retain every packet hypothesis.
It does not assert that an arbitrary configuration supplies these hypotheses.
-/
set_option pp.explicit true in
#check @Problem97.ATailTwoRadiusGridNestedEscapeTerminal.false_of_nestedEscape_packet

set_option pp.explicit true in
#check @Problem97.ATailTwoRadiusGridNestedEscapeTerminal.false_of_twoRadiusGrid_zeroCut_nestedEscape

#print axioms Problem97.ATailTwoRadiusGridNestedEscapeTerminal.false_of_nestedEscape_packet
#print axioms Problem97.ATailTwoRadiusGridNestedEscapeTerminal.false_of_twoRadiusGrid_zeroCut_nestedEscape

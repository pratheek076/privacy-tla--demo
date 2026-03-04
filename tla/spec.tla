EXTENDS Naturals, Sequences

VARIABLES db, cache, queue

(* Group variables for cleaner syntax in Spec and Fairness *)
vars == <<db, cache, queue>>

Visibility == {"PUBLIC", "PRIVATE"}

Init ==
    /\ db = "PUBLIC"
    /\ cache = "PUBLIC"
    /\ queue = << >>

DatabaseUpdate(v) ==
    /\ v \in Visibility
    /\ Len(queue) < 3 
    /\ db' = v
    /\ queue' = Append(queue, v)
    /\ UNCHANGED cache

Consume ==
    /\ Len(queue) > 0
    /\ cache' = Head(queue)
    /\ queue' = Tail(queue)
    /\ UNCHANGED db

DropMessage ==
    /\ Len(queue) > 0
    /\ queue' = Tail(queue)
    /\ UNCHANGED <<db, cache>>

Next ==
    \/ \E v \in Visibility: DatabaseUpdate(v)
    \/ Consume
    \/ DropMessage

Spec ==
    /\ Init
    /\ [][Next]_vars
    /\ WF_vars(Consume)


Consistent ==
    (Len(queue) = 0) => (cache = db)


EventualConsistency ==
    \A v \in Visibility : (db = v) ~> (cache = v)
import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time

class BTSolver:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__ ( self, gb, trail, val_sh, var_sh, cc ):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc

    # ==================================================================
    # Consistency Checks
    # ==================================================================

    # Basic consistency check, no propagation done
    def assignmentsCheck ( self ):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False
        return True

    """
        Part 1 TODO: Implement the Forward Checking Heuristic

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

		Note: remember to trail.push variables before you change their domain
        Return: true is assignment is consistent, false otherwise
    """
    def forwardChecking ( self ):
        for variable in self.network.variables:
            if variable.isAssigned():
                for neighbor in self.network.getNeighborsOfVariable(variable):
                    if variable.getAssignment() == neighbor.getAssignment():
                        return False
                    if not neighbor.isAssigned() and variable.getAssignment() in neighbor.getValues():
                        self.trail.push(neighbor)
                        neighbor.removeValueFromDomain(variable.getAssignment())
                        if neighbor.size() == 0:
                            return False
                        
                        for c in self.network.getModifiedConstraints():
                            if not c.isConsistent():
                                return False
                        
        return True

    """
        Part 2 TODO: Implement both of Norvig's Heuristics

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        (2) If a constraint has only one possible place for a value
            then put the value there.

        Note: remember to trail.push variables before you change their domain
        Return: true is assignment is consistent, false otherwise
        
        For each Unit in {rows, cols, blocks*}
            Zero Counter
            For I from 1 to N
                For each Value in DUnit[I]
                    Increment Counter[Value]
            For I from 1 to N
                If (Counter[I] = 1) then
                    Find the one domain in Unit that has I for a possible value,
                    and set that cell to I
    """
    def norvigCheck ( self ):
        for variable in self.network.variables:
            if variable.isAssigned():
                for neighbor in self.network.getNeighborsOfVariable(variable):
                    if variable.getAssignment() == neighbor.getAssignment():
                        return False
                    if not neighbor.isAssigned() and variable.getAssignment() in neighbor.getValues():
                        self.trail.push(neighbor)
                        neighbor.removeValueFromDomain(variable.getAssignment())
                        if neighbor.size() == 0:
                            return False
                        
                        for c in self.network.getModifiedConstraints():
                            if not c.isConsistent():
                                return False
                            
        n = self.gameboard.p*self.gameboard.q
        for c in self.network.getConstraints():
            counter = [0 for i in range(n)]
            for i in range(n):
                for value in c.vars[i].getValues():
                    counter[value-1] += 1
            for i in range(n):
                if counter[i] == 1:
                    for variable in c.vars:
                        if variable.getDomain().contains(i+1):
                            variable.assignValue(i+1)
                            
                            for constraint in self.network.getModifiedConstraints():
                                if not constraint.isConsistent():
                                    return False
        return True

    """
         Optional TODO: Implement your own advanced Constraint Propagation

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournCC ( self ):
        return None

    # ==================================================================
    # Variable Selectors
    # ==================================================================

    # Basic variable selector, returns first unassigned variable
    def getfirstUnassignedVariable ( self ):
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    """
        Part 1 TODO: Implement the Minimum Remaining Value Heuristic

        Return: The unassigned variable with the smallest domain
    """
    def getMRV ( self ):
        v = None
        m = float("inf")
        for variable in self.network.variables:
            if not variable.isAssigned():
                if variable.size() < m:
                    v = variable
                    m = variable.size()
        return v

    """
        Part 2 TODO: Implement the Degree Heuristic

        Return: The unassigned variable with the most unassigned neighbors
    """
    def getDegree ( self ):
        v = None
        m = float("-inf")
        for variable in self.network.variables:
            if not variable.isAssigned():
                unassigned = 0
                for neighbor in self.network.getNeighborsOfVariable(variable):
                    if not neighbor.isAssigned():
                        unassigned += 1
                if unassigned > m:
                    m = unassigned
                    v = variable
        return v

    """
        Part 2 TODO: Implement the Minimum Remaining Value Heuristic
                       with Degree Heuristic as a Tie Breaker

        Return: The unassigned variable with, first, the smallest domain
                and, second, the most unassigned neighbors
    """
    def MRVwithTieBreaker ( self ):
        v = None
        domain = float("inf")
        degree = float("-inf")
        for variable in self.network.variables:
            if not variable.isAssigned():
                unassigned = 0
                for neighbor in self.network.getNeighborsOfVariable(variable):
                    if not neighbor.isAssigned():
                        unassigned += 1
                if variable.size() == domain and unassigned > degree:
                    v = variable
                    degree = unassigned
                elif variable.size() < domain:
                    v  = variable
                    degree = unassigned
                    
        return v

    """
         Optional TODO: Implement your own advanced Variable Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVar ( self ):
        return None

    # ==================================================================
    # Value Selectors
    # ==================================================================

    # Default Value Ordering
    def getValuesInOrder ( self, v ):
        values = v.domain.values
        return sorted( values )

    """
        Part 1 TODO: Implement the Least Constraining Value Heuristic

        The Least constraining value is the one that will knock the least
        values out of it's neighbors domain.

        Return: A list of v's domain sorted by the LCV heuristic
                The LCV is first and the MCV is last
    """
    def getValuesLCVOrder ( self, v ):

        valuesDict = {k:0 for k in v.getValues()}
        for neighbor in self.network.getNeighborsOfVariable(v):
            if not neighbor.isAssigned():
                for value in neighbor.getValues():
                    if value in valuesDict:
                        valuesDict[value] += 1
        result = [k for k,v in sorted(valuesDict.items(), key=lambda item: item[1], reverse=False)]
        return result

    """
         Optional TODO: Implement your own advanced Value Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVal ( self, v ):
        return None

    # ==================================================================
    # Engine Functions
    # ==================================================================

    def solve ( self ):
        if self.hassolution:
            return

        # Variable Selection
        v = self.selectNextVariable()

        # check if the assigment is complete
        if ( v == None ):
            for var in self.network.variables:

                # If all variables haven't been assigned
                if not var.isAssigned():
                    print ( "Error" )

            # Success
            self.hassolution = True
            return

        # Attempt to assign a value
        for i in self.getNextValues( v ):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push( v )

            # Assign the value
            v.assignValue( i )

            # Propagate constraints, check consistency, recurse
            if self.checkConsistency():
                self.solve()

            # If this assignment succeeded, return
            if self.hassolution:
                return

            # Otherwise backtrack
            self.trail.undo()

    def checkConsistency ( self ):
        if self.cChecks == "forwardChecking":
            return self.forwardChecking()

        if self.cChecks == "norvigCheck":
            return self.norvigCheck()

        if self.cChecks == "tournCC":
            return self.getTournCC()

        else:
            return self.assignmentsCheck()

    def selectNextVariable ( self ):
        if self.varHeuristics == "MinimumRemainingValue":
            return self.getMRV()

        if self.varHeuristics == "Degree":
            return self.getDegree()

        if self.varHeuristics == "MRVwithTieBreaker":
            return self.MRVwithTieBreaker()

        if self.varHeuristics == "tournVar":
            return self.getTournVar()

        else:
            return self.getfirstUnassignedVariable()

    def getNextValues ( self, v ):
        if self.valHeuristics == "LeastConstrainingValue":
            return self.getValuesLCVOrder( v )

        if self.valHeuristics == "tournVal":
            return self.getTournVal( v )

        else:
            return self.getValuesInOrder( v )

    def getSolution ( self ):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)

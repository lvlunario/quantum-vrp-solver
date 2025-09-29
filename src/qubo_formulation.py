from qiskit_optimization.applications import Tsp
from src.problem import create_vrp_instance

def create_qubo_from_vrp():
    """
    Converts the VRP instance into a QUBO problem.
    For simplicity, we model this as a Traveling Salesperson Problem (TSP),
    as VRP is a generalization of TSP.
    """
    _, dist_matrix = create_vrp_instance()
    num_nodes = len(dist_matrix)

    # Using Qiskit's built-in TSP application class
    tsp_problem = Tsp(dist_matrix)

    # Convert to a quadratic program, which is the QUBO representation
    qp = tsp_problem.to_quadratic_program()

    print("Quadratic Program Created:")
    print(qp.prettyprint())

    return qp

if __name__ == '__main__':
    create_qubo_from_vrp()
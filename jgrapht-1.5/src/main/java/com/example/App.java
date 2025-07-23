package com.example;

import org.jgrapht.*;
import org.jgrapht.graph.*;
import org.jgrapht.alg.shortestpath.*;

public class App 
{
    public static void main( String[] args )
    {
        // Creazione del grafo
        Graph<String, DefaultWeightedEdge> graph = new SimpleDirectedWeightedGraph<>(DefaultWeightedEdge.class);

        // Aggiunta dei vertici
        graph.addVertex("A");
        graph.addVertex("B");
        graph.addVertex("C");

        // Aggiunta degli archi con pesi
        graph.setEdgeWeight(graph.addEdge("A", "B"), 1.0);
        graph.setEdgeWeight(graph.addEdge("B", "C"), 2.0);
        graph.setEdgeWeight(graph.addEdge("A", "C"), 4.0);

        // Algoritmo di Dijkstra per il percorso più breve
        DijkstraShortestPath<String, DefaultWeightedEdge> dijkstraAlg =
                new DijkstraShortestPath<>(graph);
        GraphPath<String, DefaultWeightedEdge> path = dijkstraAlg.getPath("A", "C");

        // Stampa il percorso più breve
        System.out.println("Percorso più breve da A a C: " + path);
    }
}

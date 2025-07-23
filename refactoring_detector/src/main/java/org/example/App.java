package org.example;


import org.eclipse.jgit.lib.Repository;
import org.refactoringminer.api.GitHistoryRefactoringMiner;
import org.refactoringminer.api.GitService;
import org.refactoringminer.api.Refactoring;
import org.refactoringminer.api.RefactoringHandler;
import org.refactoringminer.rm1.GitHistoryRefactoringMinerImpl;
import org.refactoringminer.util.GitServiceImpl;

import java.io.File;
import java.util.List;

/**
 * Hello world!
 *
 */
public class App 
{
    public static void main( String[] args ) throws Exception
    {
        // storia dei refactoring in una repo github
        GitService gitService = new GitServiceImpl();
        GitHistoryRefactoringMiner miner = new GitHistoryRefactoringMinerImpl();

        Repository repo = gitService.cloneIfNotExists(
                "tmp/refactoring-jgrapht-example",
                "https://github.com/jgrapht/jgrapht.git");

        miner.detectAll(repo, "master", new RefactoringHandler() {
            @Override
            public void handle(String commitId, List<Refactoring> refactorings) {
                System.out.println("Refactorings at " + commitId);
                for (Refactoring ref : refactorings) {
                    System.out.println(ref.toString());
                }
            }
        });
         /*
        GitHistoryRefactoringMiner miner = new GitHistoryRefactoringMinerImpl();
        // You must provide absolute paths to the directories. Relative paths will cause exceptions.
        File dir1 = new File("/home/federico/JGraphT_Test/jgrapht-1.4/jgrapht");
        File dir2 = new File("/home/federico/JGraphT_Test/jgrapht-1.5/jgrapht");
        miner.detectAtDirectories(dir1, dir2, new RefactoringHandler() {
            @Override
            public void handle(String commitId, List<Refactoring> refactorings) {
                System.out.println("Refactorings at " + commitId);
                for (Refactoring ref : refactorings) {
                    System.out.println(ref.toString());
                }
            }
        });*/
    }
}

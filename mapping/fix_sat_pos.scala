import java.io.File
import java.nio.file.Files

val wnhome = "../../../Downloads/WordNet-3.0/dict/"

val nouns = for(line <- io.Source.fromFile(wnhome + "data.noun").getLines if !line.startsWith(" ")) yield { line.slice(0,8)+"-n" }
val advs = for(line <- io.Source.fromFile(wnhome + "data.adv").getLines if !line.startsWith(" ")) yield { (line.slice(0,8)+"-r") }
val adjs = for(line <- io.Source.fromFile(wnhome + "data.adj").getLines if !line.startsWith(" ")) yield { (line.slice(0,8)+"-" + line(12)) }
val verbs = for(line <- io.Source.fromFile(wnhome + "data.verb").getLines if !line.startsWith(" ")) yield { (line.slice(0,8)+"-v") }

val all = (nouns ++ advs ++ adjs ++ verbs).toSet

val mapped = io.Source.fromFile("wn30-31-release.csv").getLines.map(_.slice(0,10)).toSet

val tofix = (all -- mapped).map(_.replaceAll("s$","a"))

Files.copy(new File("wn30-31-release.csv").toPath,new File("tmp").toPath)

val out = new java.io.PrintWriter("wn30-31-release.csv")

for(line <- io.Source.fromFile("tmp").getLines) {
  val id = line.slice(0,10)
  if(tofix contains id) {
    out.println(line.slice(0,9) + "s" + line.drop(10))
  } else {
    out.println(line)
  }
}
out.flush
out.close

Files.delete(new File("tmp").toPath)
